import datetime

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
# matplotlibの日本語化・importするだけで良い
# import japanize_matplotlib # type: ignore
import mplfinance as mpf # type: ignore

import utils
import config


def analyze_quotes(codes):
    """
    メインから呼び出される関数

    Args:
        codes: 銘柄コードのリスト
    """

    print("=== Analyze quotes ===")

    # 日付の設定
    date = config.analysys_date

    # 財務情報を読み込み
    df_fins = pd.read_csv(f"data/{date}/fins/fins_org.csv", dtype={2: str})

    # topixの株価情報を読み込み
    df_topix = pd.read_csv(f"data/{date}/quotes/0028.csv", dtype={2: str})

    # 会社名と銘柄コードの対応を辞書型で取得
    code_name_dict = make_code_company_name_dict(date)

    # 銘柄コード毎に処理
    for i, code in enumerate(codes, start=1):

        # 財務情報と株価情報を結合
        df_merged = merge_fins_and_stock(
            df_fins=df_fins, df_topix=df_topix, code=code, date=date
        )

        # PER・PBR・ROE・時価総額　200日平均線　等の指標を計算
        df_calculated = set_calculated_values(df_merged)

        # 理論株価を計算
        df_result = calc_theoretical_stock_price(df_calculated)

        # 分析チャートを作成
        plot_chart_matplotlib(df_result, code_name_dict[code])

        # ローソクチャートを作成
        # generate_candlestick_chart(df_result, code , 30)

    # PDFファイルの作成
    try:
        utils.images_to_pdf(f"data/{date}/images", f"data/{date}/report.pdf")
        print("PDF created")
    except Exception as e:
        print(f"failed to create pdf: {e}")


def merge_fins_and_stock(
    df_fins: pd.DataFrame, df_topix: pd.DataFrame, code: str, date: datetime
) -> pd.DataFrame:
    """
    株価情報と財務情報を結合する関数

    Args:
        df_fins: 財務情報のデータフレーム
        df_topix: TOPIXのデータフレーム
        code: 銘柄コード
    Returns:
        df_merged: 結合したデータフレーム
    """

    # codeの財務情報だけを摘出
    df_fins_extracted = df_fins[df_fins["LocalCode"] == code]

    # 株価情報を読み込み
    df_quotes = pd.read_csv(f"data/{date}/quotes/{code}.csv")

    # 株価情報とtopixの株価情報を結合
    df_stock = pd.merge(
        df_quotes, df_topix, on="Date", how="left", suffixes=("_quotes", "_topix")
    )

    # 財務情報と株価情報を結合
    df_merged = pd.merge(
        df_stock,
        df_fins_extracted,
        left_on="Date",
        right_on="DisclosedDate",
        how="left",
    )

    # 欠損値を補完
    df_merged = df_merged.fillna(method="ffill")

    return df_merged


def make_code_company_name_dict(date: datetime) -> dict:
    """
    銘柄コードと会社名の対応を辞書型で返す関数

    Args:
        date: 日付
    Returns:
        dict: 銘柄コードと会社名の対応を辞書型で返す
    """

    # 基本情報を読み込み
    df_listed = pd.read_csv(f"data/{date}/listed_info.csv")

    # 銘柄コードと会社名の対応を辞書型で返す
    return dict(zip(df_listed["Code"], df_listed["CompanyName"]))


def plot_chart_matplotlib(df, company_name):
    date = config.analysys_date
    image_path = f"data/{date}/images"
    utils.generate_dir_if_not_exists(image_path)
    code = df["LocalCode"].dropna().iloc[0]
    title = f"{code} {company_name}"

    # 日付データの型を確認し、必要に応じて変換
    if not pd.api.types.is_datetime64_any_dtype(df["Date"]):
        df["Date"] = pd.to_datetime(df["Date"])

    # 4行1列のグラフを作成
    fig, axes = plt.subplots(nrows=4, ncols=1, figsize=(6, 9))
    fig.suptitle(title)

    # グラフ1 (株価、理論株価、理論株価上限)
    axes[0].plot(df["Date"], df["AdjustmentClose"], label="Price")
    axes[0].plot(df["Date"], df["TheoreticalStockPrice"], label="Theoretical")
    axes[0].plot(df["Date"], df["TheoreticalStockPriceUpperLimit"], label="Upper Limit")
    axes[0].plot(df["Date"], df["SMA_200"], label="SMA-200")
    axes[0].legend(loc="upper left", borderaxespad=0, fontsize=9)
    axes[0].grid(True)

    # グラフ2 (出来高)
    df["Smoothed_volume"] = df["Smoothed_volume"] / 10**4
    axes[1].plot(df["Date"], df["Smoothed_volume"], label="Volume")
    axes[1].legend(loc="upper left", borderaxespad=0, fontsize=9)
    axes[1].set_ylabel("万株")
    axes[1].grid(True)

    # グラフ3 (PER、PBR、ROE)
    axes[2].plot(df["Date"], df["PER"], label="PER")
    axes[2].plot(df["Date"], df["PBR"], label="PBR")
    axes[2].plot(df["Date"], df["ROE"], label="ROE")
    axes[2].legend(loc="upper left", borderaxespad=0, fontsize=9)
    axes[2].grid(True)

    # グラフ5 (当期純利益)
    axes[3].plot(df["Date"], df["Profit"] / 10**9, label="Profit")
    axes[3].legend(loc="upper left", borderaxespad=0, fontsize=9)
    axes[3].set_ylabel("10億円")
    axes[3].grid(True)

    # X軸のフォーマットを年のみに設定
    for ax in axes:
        ax.xaxis.set_major_locator(mpl.dates.AutoDateLocator(minticks=2, maxticks=7))
        ax.xaxis.set_major_formatter(mpl.dates.DateFormatter("%Y-%m"))  # 年のみを表示
        plt.setp(ax.get_xticklabels(), rotation=0, fontsize=10)

    # フォント設定の確認
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Hiragino Maru Gothic Pro', 'Yu Gothic', 'Meirio', 'Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']

    fig.savefig(f"{image_path}/{code}_a.png")
    plt.close("all")

def generate_candlestick_chart(df: pd.DataFrame, code: str, tail: int):
    """ローソクチャートを作成し、pngで保存する

    Args:
        df (pd.DataFrame): データ
        code (str): 銘柄コード pngのファイル名に使用
        name (str): 企業名 pngのファイル名に使用
    """

    # ローソクチャート用にDFをコピー
    df_candle = df.tail(tail).copy()

    # Dateをインデックスに設定
    df_candle["Date"] = pd.to_datetime(df["Date"])
    df_candle.set_index("Date", inplace=True)

    df_candle["Open"] = df_candle["AdjustmentOpen"]
    df_candle["High"] = df_candle["AdjustmentHigh"]
    df_candle["Low"] = df_candle["AdjustmentLow"]
    df_candle["Close"] = df_candle["AdjustmentClose"]

# 描画設定と保存
    image_path = f"data/{config.analysys_date}/images/{code}_candle.png"
    save_settings = {"fname": image_path, "dpi": 100, "pad_inches": 0.25}
    mpf.plot(
        df_candle,
        type='candle',
        volume=True,
        mav=(5, 25),
        style='charles',
        savefig=save_settings
    )

def set_calculated_values(df):
    df = set_PER_value(df)
    df = set_PBR_value(df)
    df = set_ROE_value(df)
    df = set_market_cap(df)
    df = set_smoothed_volume(df)
    df = set_index_of_adjustment_close_and_topix(df)
    df = set_200days_moving_average(df)

    return df


def calc_theoretical_stock_price(df):
    # 割引率を計算
    df = set_discount_rate(df)
    # ROAを計算
    df = set_ROA(df)
    # ROAの上限を設定
    df = limit_ROA_value(df)
    # リスク評価率を計算
    df = set_risk_assesment_rate(df)
    # 財務レバレッジ調整を計算
    df = set_financial_leverage_adjustment(df)
    # 資産価値を計算
    df = set_asset_value(df)
    # 事業価値を計算
    df = set_business_value(df)
    # 理論株価を計算
    df = set_theoretical_stock_price(df)

    return df


def set_discount_rate(df):
    conditions = [
        df["EquityToAssetRatio"] >= 0.8,
        (df["EquityToAssetRatio"] >= 0.67) & (df["EquityToAssetRatio"] < 0.8),
        (df["EquityToAssetRatio"] >= 0.5) & (df["EquityToAssetRatio"] < 0.67),
        (df["EquityToAssetRatio"] >= 0.33) & (df["EquityToAssetRatio"] < 0.5),
        (df["EquityToAssetRatio"] >= 0.1) & (df["EquityToAssetRatio"] < 0.33),
        (df["EquityToAssetRatio"] < 0.1),
    ]

    choices = [
        0.8,
        0.75,
        0.7,
        0.65,
        0.6,
        0.5,
    ]

    df["DiscountRate"] = np.select(conditions, choices, default=np.nan)

    return df


def set_PER_value(df):
    # 株式分割されると値がジャンプするので最新の発行済株数で計算
    latest_shares = df["NumberOfIssuedAndOutstandingSharesAtTheEndOfFiscalYearIncludingTreasuryStock"].iloc[-1]
    df["PER"] = df["AdjustmentClose"] / (df["ForecastProfit"] / latest_shares)
    return df


def set_PBR_value(df):
    # 株式分割されると値がジャンプするので最新の発行済株数で計算
    latest_shares = df["NumberOfIssuedAndOutstandingSharesAtTheEndOfFiscalYearIncludingTreasuryStock"].iloc[-1]
    df["PBR"] = df["AdjustmentClose"] / (df["Equity"] / latest_shares)
    return df


def set_ROE_value(df):
    df["ROE"] = df["ForecastProfit"] / df["Equity"] * 100
    return df


def set_market_cap(df):
    df["MarketCap"] = df["AdjustmentClose"] * df["AverageNumberOfShares"]
    return df


def set_ROA(df):
    df["ROA"] = df["ForecastProfit"] / df["TotalAssets"]
    return df


def limit_ROA_value(df):
    conditions = [df["ROA"] >= 0.3]

    choices = [0.3]

    df["ROA"] = np.select(conditions, choices, default=df["ROA"])

    return df


def set_financial_leverage_adjustment(df):
    # 計算用のカラムを追加
    df["TempValue"] = df["TotalAssets"] + 0.33

    # 計算用のカラムの上限と下限を設定
    conditions = [
        df["TempValue"] < 0.66,
        df["TempValue"] > 1.00,
    ]
    choices = [
        0.66,
        1.00,
    ]

    df["TempValue"] = np.select(conditions, choices, default=df["TempValue"])

    # 財務レバレッジ調整を計算
    df["FinancialLeverageAdjustment"] = 1 / df["TempValue"]

    # 不要なカラムを削除
    df = df.drop(columns=["TempValue"])

    return df


def set_risk_assesment_rate(df):
    conditions = [
        df["PBR"] >= 0.5,
        (df["PBR"] >= 0.41) & (df["PBR"] < 0.49),
        (df["PBR"] >= 0.34) & (df["PBR"] < 0.40),
        (df["PBR"] >= 0.25) & (df["PBR"] < 0.33),
        (df["PBR"] >= 0.21) & (df["PBR"] < 0.25),
        (df["PBR"] >= 0.04) & (df["PBR"] < 0.20),
        df["PBR"] < 0.04,
    ]

    choices = [
        1,
        0.8,
        0.66,
        0.50,
        0.33,
        0.15,
        0.02,
    ]

    df["RiskAssesmentRate"] = np.select(conditions, choices, default=np.nan)

    return df


def set_asset_value(df):
    df["AssetValue"] = df["PBR"] * df["DiscountRate"]

    return df


def set_business_value(df):
    # 株式分割されると値がジャンプするので最新の発行済株数で計算
    latest_shares = df["NumberOfIssuedAndOutstandingSharesAtTheEndOfFiscalYearIncludingTreasuryStock"].iloc[-1]
    df["BusinessValue"] = (
        (df["ForecastProfit"] / latest_shares) # EPS
        * df["ROA"]
        * 150
        * df["FinancialLeverageAdjustment"]
    )

    return df


def set_theoretical_stock_price(df):
    df["TheoreticalStockPrice"] = (df["BusinessValue"] + df["AssetValue"]) * df[
        "RiskAssesmentRate"
    ]
    # 理論株価上限
    df["TheoreticalStockPriceUpperLimit"] = df["TheoreticalStockPrice"] * 2

    return df

def set_200days_moving_average(df):
    df["SMA_200"] = df["AdjustmentClose"].rolling(window=200).mean()
    return df


def set_index_of_adjustment_close_and_topix(df):
    """
    時価総額とtopixの増減を最初を1として比較
    """
    # 時価総額とtopixの増減を最初を1とする
    df["AdjustmentClose_indexed"] = (
        df["AdjustmentClose"] / df["AdjustmentClose"].dropna().iloc[0]
    )
    df["Close_topix_indexed"] = df["Close_topix"] / df["Close_topix"].dropna().iloc[0]

    return df


def is_worse_than_topix(df):
    """
    時価総額とtopixの増減を比較
    """
    # 日付順にソート
    df = df.sort_values(by="Date")

    # 最新の時価総額とtopixの増減を比較
    return df["AdjustmentClose_indexed"].iloc[-1] < df["Close_topix_indexed"].iloc[-1]


def ratio_against_topix(df):
    """
    株価の増加がtopixに対してどれだけかを計算
    """
    # 日付順にソート
    df = df.sort_values(by="Date")

    # 最新の時価総額とtopixの増減を比較
    return df["AdjustmentClose_indexed"].iloc[-1] / df["Close_topix_indexed"].iloc[-1]


def set_smoothed_volume(df):
    """
    出来高の移動平均を計算
    """
    df["Smoothed_volume"] = (
        df["Volume"].rolling(window=config.volume_window_size).mean()
    )

    return df
