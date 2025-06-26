import datetime
import os
import subprocess

import pandas as pd
from PIL import Image


def check_file_exists(file_path):
    """
    指定したディレクトリに指定したファイル名のファイルが存在するかどうかを調べる関数

    file_path: ファイルのパス
    return: ファイルが存在する場合はTrue、そうでない場合はFalse
    """

    return os.path.exists(file_path)


def prepare_date_dir(date):
    """
    今日の日付のディレクトリが無い場合は作成する関数
    """
    if date is None:
        date = datetime.date.today()

    file_dir = f"data/{date}"
    generate_dir_if_not_exists(file_dir)
    generate_dir_if_not_exists(f"{file_dir}/quotes")
    generate_dir_if_not_exists(f"{file_dir}/images")
    generate_dir_if_not_exists(f"{file_dir}/fins")


def generate_dir_if_not_exists(path):
    """
    ディレクトリが存在しない場合はディレクトリを作成する関数

    Args:
        path: 作成するディレクトリのパス
    """
    if not os.path.exists(path):
        os.makedirs(path)


def generate_today_data_dir_if_not_exists(path):
    """
    ディレクトリが存在しない場合はディレクトリを作成する関数

    Args:
        path: 作成するディレクトリのパス
    """
    if not os.path.exists(path):
        os.makedirs(path)


def save_as_csv(df, directory, filename):
    """
    データフレームをCSVファイルとして保存する関数

    Args:
        df: 保存するデータフレーム
        path: 保存するディレクトリのパス
        suffix: ファイル名のサフィックス
    """
    # ファイル名を生成
    filename = f"{filename}.csv"

    # ファイルパスを生成
    file_path = os.path.join(directory, filename)

    # ファイルを保存
    df.to_csv(file_path, index=False)


def extract_columns(df: pd.DataFrame, columns: list):
    """
    必要なカラムのみを抽出する関数

    Args:
        df: データフレーム
        columns: カラム名のリスト
    Returns:
        抽出したデータフレーム
    """
    try:
        return df[columns]
    except Exception as e:
        print(f"failed to extract columns @extract_columns: {e}")
        return None


def filter_by_column_name_and_data(df: pd.DataFrame, column_name: str, data: any):
    """
    指定したカラムがdataに一致した行だけを取得する関数

    Args:
        df: データフレーム
        column_name: カラム名
        data: 指定したカラムのデータ
    """
    # 年度末のデータだけを取得
    mask = df[column_name].astype(str).str.contains(data, na=False)

    return df[mask]


def extract_non_duplicated_values(df, column_name):
    """
    指定したカラムの重複を削除した値をリストで返す関数

    Args:
        df: データフレーム
        column_name: カラム名
    return: 重複を削除した値のリスト
    """
    return df[column_name].drop_duplicates().tolist()


def images_to_pdf(image_dir_path: str, output_pdf_path: str):
    """
    指定したディレクトリ内の画像ファイルをPDFファイルに変換する関数

    Args:
        image_dir_path: 画像ファイルのディレクトリ
        output_pdf_path: 出力するPDFファイルのパス
    Retunrs:
        None
    """

    # dir_path から画像ファイルのリストを取得
    images = [
        os.path.join(image_dir_path, f)
        for f in os.listdir(image_dir_path)
        if f.endswith((".png", ".jpg", ".jpeg"))
    ]
    # 画像ファイルをソート（必要に応じて）
    images.sort()

    # 画像ファイルのリストが空でない場合
    if images:
        # 最初の画像を開いて他の画像を追加する
        with Image.open(images[0]) as img:
            img_list = [Image.open(image).convert("RGB") for image in images[1:]]
            img.save(
                output_pdf_path,
                "PDF",
                resolution=100.0,
                save_all=True,
                append_images=img_list,
            )


def convert_to_numeric(df, columns):
    """
    データフレームの指定したカラムを数値に変換する関数
    df: データフレーム
    columns: 数値に変換するカラムのリスト
    return: 数値に変換したデータフレーム
    """
    df[columns] = df[columns].apply(pd.to_numeric, errors="coerce")

    return df


def open_by_finder(path: str):
    """
    指定したパスをFinderで開く関数

    Args:
        path: パス
    """

    try:
        subprocess.run(["open", path], check=True)
    except Exception as e:
        print(f"Failed to open {path}: {e}")
