import streamlit as st
from PIL import Image
from rembg import remove
import os
import tempfile
import cv2
import numpy as np

def merge_images(background_image, overlay_image, overlay_scale, overlay_position):
   """
   背景画像と重ねる画像を合成する関数
   Parameters:
       background_image (PIL.Image.Image): 背景画像
       overlay_image (PIL.Image.Image): 重ねる画像
       overlay_scale (float): 重ねる画像のサイズ倍率
       overlay_position (tuple): 重ねる画像の左上の座標 (x, y)
   Returns:
       PIL.Image.Image: 合成された画像
   """
   # 背景を削除して出力画像を生成
   overlay_image_no_bg = remove(overlay_image.convert("RGBA"))  # アルファチャンネルを保持するために"RGBA"に変換
   # 重ねる画像をリサイズ
   overlay_width, overlay_height = overlay_image_no_bg.size
   overlay_image_no_bg = overlay_image_no_bg.resize((int(overlay_width * overlay_scale), int(overlay_height * overlay_scale)))
   # 背景画像に重ねる画像を重ねる
   background_image_copy = background_image.copy()  # 背景画像のコピーを作成
   background_image_copy.paste(overlay_image_no_bg, overlay_position, overlay_image_no_bg)  # アルファチャンネルを渡す
   return background_image_copy
def main():
   """
   Streamlitアプリのメイン関数。
   """
   st.title("Stuffed toy camera")
   st.write("画像を選んでください")
   # サイドバーにモノクロ機能を追加
   monochrome_background = st.sidebar.checkbox("モノクロ")
   # サイドバーにセピア変換
   sepia_background = st.sidebar.checkbox("暖色")
   # サイドバーに減色変換
   gensyoku_background = st.sidebar.checkbox("寒色")
   # 背景画像のアップロード
   background_image = st.file_uploader("背景の画像をアップロードしてください", type=["jpg", "png"])
   if background_image:
       background_image = Image.open(background_image)
       # モノクロ変換の実装
       if monochrome_background:
           background_image = background_image.convert("L")  # グレースケールに変換
       # セピア変換の実装    
       if sepia_background:
           sepia_image = background_image.convert("RGB")
           r, g, b = sepia_image.split()
           r = r.point(lambda x: x * 1.1)
           g = g.point(lambda x: x * 0.9)
           b = b.point(lambda x: x * 0.7)
           sepia_image = Image.merge("RGB", (r, g, b))
           background_image = sepia_image
        # ネガポジ変換の実装
       if gensyoku_background:
           gensyoku_image = cv2.bitwise_not(np.array(background_image))
           background_image = Image.fromarray(gensyoku_image)
               
       # 重ねる画像のアップロード
       overlay_image = st.file_uploader("重ねる画像をアップロードしてください", type=["jpg", "png"])
       if overlay_image:
           overlay_image = Image.open(overlay_image)
           # 重ねる画像のサイズを変更するためのスライダー
           overlay_scale = st.slider("重ねる画像のサイズ", 0.1, 2.0, 1.0)
           # 重ねる画像の横位置を調整するためのスライダー
           overlay_position_x = st.slider("重ねる画像の横位置", 0, background_image.width, 0)
           overlay_position_y = st.slider("重ねる画像の縦位置", 0, background_image.height, 0)
           overlay_position = (overlay_position_x, overlay_position_y)
           # 画像を合成する
           merged_image = merge_images(background_image, overlay_image, overlay_scale, overlay_position)
           # 合成した画像を表示
           st.image(merged_image, caption='合成結果', use_column_width=True)
           # 保存ボタン
           if st.button("保存"):
               with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                   merged_image.save(tmp_file.name)
                   st.download_button(
                       label="ここをクリックして画像をダウンロード",
                       data=open(tmp_file.name, "rb").read(),
                       file_name="merged_image.png",
                       mime="image/png",
                   )
if __name__ == "__main__":
   main()
