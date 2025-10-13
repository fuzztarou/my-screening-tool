"""
プロットロジックを担当するクラス

各種データのプロット処理を個別のメソッドとして実装します。
"""

import pandas as pd
from matplotlib.axes import Axes


class Plotter:
    """プロット処理を担当するクラス"""

    def plot_price_lines(self, ax: Axes, df: pd.DataFrame) -> None:
        """株価の各種ラインをプロット"""
        ax.plot(
            df["Date"],
            df["AdjustmentClose"],
            label="Stock Price",
            linewidth=1.2,
            color="blue",
        )
        ax.plot(
            df["Date"],
            df["TheoreticalStockPrice"],
            label="Theoretical Price",
            linestyle="--",
            linewidth=1,
            color="blue",
        )
        ax.plot(
            df["Date"],
            df["TheoreticalStockPriceUpperLimit"],
            label="Theoretical Upper",
            linestyle=":",
            linewidth=1,
            color="blue",
        )

    def plot_volume_bars(self, ax: Axes, df: pd.DataFrame, alpha: float = 0.6) -> None:
        """出来高のバーと移動平均線をプロット"""
        volume_10k = df["Volume"] / 10000
        volume_ma25 = df["Volume"].rolling(window=25, min_periods=1).mean() / 10000
        volume_ma75 = df["Volume"].rolling(window=75, min_periods=1).mean() / 10000

        ax.bar(
            df["Date"], volume_10k, color="green", alpha=alpha, label="Volume", width=1
        )
        ax.plot(
            df["Date"],
            volume_ma25,
            label="volume 25-day MA",
            color="green",
            linewidth=1,
            alpha=alpha * 1.5,
        )
        ax.plot(
            df["Date"],
            volume_ma75,
            label="volume 75-day MA",
            color="green",
            linewidth=1,
            linestyle="--",
            alpha=alpha * 1.5,
        )

    def plot_sales(self, ax: Axes, df: pd.DataFrame) -> None:
        """売上高をプロット (実績と予想)"""
        # 売上高データを億円単位に変換
        df = df.copy()
        df["NetSales_100M"] = df["NetSales"] / 1e8
        df["ForecastNetSales_100M"] = df["ForecastNetSales"] / 1e8

        # 実績売上高
        ax.step(
            df["Date"],
            df["NetSales_100M"],
            where="post",
            label="Net Sales (Actual)",
            linewidth=1.5,
            color="purple",
        )

        # 予想売上高
        ax.step(
            df["Date"],
            df["ForecastNetSales_100M"],
            where="post",
            label="Net Sales (Forecast)",
            linestyle="--",
            linewidth=1.5,
            color="red",
            alpha=0.7,
        )

    def plot_operating_profit(self, ax: Axes, df: pd.DataFrame) -> None:
        """営業利益をプロット (実績と予想)"""
        # 営業利益データを億円単位に変換
        df = df.copy()
        df["OperatingProfit_100M"] = df["OperatingProfit"] / 1e8
        df["ForecastOperatingProfit_100M"] = df["ForecastOperatingProfit"] / 1e8

        # 実績営業利益
        ax.step(
            df["Date"],
            df["OperatingProfit_100M"],
            where="post",
            label="Operating Profit (Actual)",
            linewidth=1.5,
            color="green",
        )

        # 予想営業利益
        ax.step(
            df["Date"],
            df["ForecastOperatingProfit_100M"],
            where="post",
            label="Operating Profit (Forecast)",
            linestyle="--",
            linewidth=1.5,
            color="red",
            alpha=0.7,
        )

    def plot_net_profit(self, ax: Axes, df: pd.DataFrame) -> None:
        """純利益をプロット (実績と予想)"""
        # 利益データを億円単位に変換
        df = df.copy()
        df["Profit_100M"] = df["Profit"] / 1e8
        df["ForecastProfit_100M"] = df["ForecastProfit"] / 1e8

        # 実績利益
        ax.step(
            df["Date"],
            df["Profit_100M"],
            where="post",
            label="Net Profit (Actual)",
            linewidth=1.5,
            color="blue",
        )

        # 予想利益
        ax.step(
            df["Date"],
            df["ForecastProfit_100M"],
            where="post",
            label="Net Profit (Forecast)",
            linestyle="--",
            linewidth=1.5,
            color="red",
            alpha=0.7,
        )

    def plot_per(self, ax: Axes, df: pd.DataFrame) -> None:
        """PERをプロット"""
        ax.plot(df["Date"], df["PER"], label="PER", color="blue", linewidth=1.5)

    def plot_pbr(self, ax: Axes, df: pd.DataFrame) -> None:
        """PBRをプロット"""
        ax.plot(df["Date"], df["PBR"], label="PBR", color="green", linewidth=1.5)

    def plot_psr(self, ax: Axes, df: pd.DataFrame) -> None:
        """PSRをプロット"""
        ax.plot(df["Date"], df["PSR"], label="PSR", color="purple", linewidth=1.5)

    def plot_roe(self, ax: Axes, df: pd.DataFrame) -> None:
        """ROEをプロット"""
        ax.plot(
            df["Date"], df["ROE"] * 100, label="ROE(%)", color="orange", linewidth=1.5
        )

    def plot_roa(self, ax: Axes, df: pd.DataFrame) -> None:
        """ROAをプロット"""
        ax.plot(
            df["Date"],
            df["ROA"] * 100,
            label="ROA(%)",
            color="orange",
            linestyle="--",
            linewidth=1,
        )

    def plot_peg_ratio(self, ax: Axes, df: pd.DataFrame) -> None:
        """PEG Ratioをプロット (NaN値をスキップ)"""
        # NaN値を除外
        df_valid = df[df["PEG"].notna()].copy()
        if not df_valid.empty:
            ax.plot(
                df_valid["Date"],
                df_valid["PEG"],
                label="PEG Ratio",
                color="red",
                linewidth=1.5,
            )

    def plot_operating_profit_growth_rate(self, ax: Axes, df: pd.DataFrame) -> None:
        """営業利益成長率をプロット"""
        ax.plot(
            df["Date"],
            df["OperatingProfitGrowthRate"],
            label="Op. Profit Growth(%)",
            color="darkgreen",
            linewidth=1.5,
        )

    def plot_operating_margin(self, ax: Axes, df: pd.DataFrame) -> None:
        """営業利益率(実績)をプロット"""
        ax.plot(
            df["Date"],
            df["OperatingMargin"],
            label="Operating Margin (Actual)",
            linewidth=1.5,
            color="darkgreen",
        )

    def plot_forecast_operating_margin(self, ax: Axes, df: pd.DataFrame) -> None:
        """営業利益率(予想)をプロット"""
        ax.plot(
            df["Date"],
            df["ForecastOperatingMargin"],
            label="Operating Margin (Forecast)",
            linestyle="--",
            linewidth=1.5,
            color="red",
            alpha=0.7,
        )

    def plot_net_margin(self, ax: Axes, df: pd.DataFrame) -> None:
        """純利益率(実績)をプロット"""
        ax.plot(
            df["Date"],
            df["NetMargin"],
            label="Net Margin (Actual)",
            linewidth=1.5,
            color="darkblue",
        )

    def plot_forecast_net_margin(self, ax: Axes, df: pd.DataFrame) -> None:
        """純利益率(予想)をプロット"""
        ax.plot(
            df["Date"],
            df["ForecastNetMargin"],
            label="Net Margin (Forecast)",
            linestyle="--",
            linewidth=1.5,
            color="red",
            alpha=0.7,
        )
