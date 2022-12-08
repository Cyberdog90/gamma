import PySimpleGUI as gui
import numpy as np
import cv2 as cv
import configparser as cfg
from typing import List
from time import time
from os.path import basename


class Main:
    def __init__(self):
        self.cfg = cfg.ConfigParser()
        self.cfg.read("config.ini")
        self.gamma = float(self.cfg["VALUES"]["gamma"])

        self.image = np.zeros((256, 256, 3), np.uint8)
        self.edited = np.zeros((256, 256, 1), np.uint8)
        self.original = np.zeros((256, 256, 3), np.uint8)
        gui.theme("DarkBlue17")
        self.window = gui.Window(title="image converter",
                                 layout=self.layout(),
                                 element_justification="c")
        self.event = None
        self.value = None
        self.file_name = ""

    def main(self) -> None:
        while True:
            self.event, self.value = self.window.read(timeout=1000 // 60)
            if self.event is None:
                break
            if self.event == "devLoad":
                self.gamma = float(self.cfg["VALUES"]["gamma"])
                self.window["devGamma"].update(self.gamma)

            if self.event == "devSave":
                self.cfg["VALUES"]["gamma"] = str(self.value["devGamma"])
                with open("config.ini", "w") as f:
                    self.cfg.write(f)

            if self.event == "saveFig":
                self.save()

            self.dev_mode_switch()
            if self.value["fileText"] != self.file_name:
                self.original = self.image = cv.imread(self.value["fileText"])
                self.image = cv.resize(self.image, dsize=(256, 256))
                self.file_name = self.value["fileText"]
                self.window["baseImage"].update(data=cv.imencode('.png', self.image)[1].tobytes())
            self.processing()
        self.window.close()

    def layout(self) -> List[List]:
        return [
            [gui.Image(data=cv.imencode('.png', self.image)[1].tobytes(), size=(256, 256), key="baseImage"),
             gui.Image(data=cv.imencode('.png', self.edited)[1].tobytes(), size=(256, 256), key="editedImage")],
            [gui.InputText(key="fileText", disabled=True),
             gui.FileBrowse(button_text="画像読み込み", key="file", target="fileText",
                            file_types=(("画像ファイル", ".png"), ("画像ファイル", ".jpg"), ("画像ファイル", ".jpeg"))),
             gui.Button(button_text="画像保存", key="saveFig")],
            [gui.Text(text="ガンマ値"),
             gui.Slider(range=(0.0, 10.0), resolution=.05, default_value=1.0, size=(40, 15),
                        orientation="h", key="gamma")],

            [gui.Checkbox(text="開発者モード", default=False, key="devMode"),
             gui.Button(button_text="セーブ", disabled=True, key="devSave"),
             gui.Button(button_text="ロード", disabled=True, key="devLoad")],
            [gui.Text(text="ガンマ値"),
             gui.Slider(range=(0.0, 10.0), resolution=.05, default_value=self.gamma, disabled=True, size=(40, 15),
                        orientation="h", key="devGamma")]
        ]

    def processing(self):
        self.edited = cv.cvtColor(self.image, cv.COLOR_BGR2GRAY)

        look_up_table = np.empty((1, 256), np.uint8)
        for i in range(256):
            look_up_table[0, i] = np.clip(pow(i / 255.0, self.value["gamma"]) * 255.0, 0, 255)
        self.edited = cv.LUT(self.edited, look_up_table)

        look_up_table = np.empty((1, 256), np.uint8)
        for i in range(256):
            look_up_table[0, i] = np.clip(pow(i / 255.0, self.value["devGamma"]) * 255.0, 0, 255)
        self.edited = cv.LUT(self.edited, look_up_table)

        self.window["editedImage"].update(data=cv.imencode('.png', self.edited)[1].tobytes())

    def dev_mode_switch(self):
        if self.value["devMode"]:
            self.window["devSave"].update(disabled=False)
            self.window["devLoad"].update(disabled=False)
            self.window["devGamma"].update(disabled=False)
        else:
            self.window["devSave"].update(disabled=True)
            self.window["devLoad"].update(disabled=True)
            self.window["devGamma"].update(disabled=True)

    def save(self):
        image = cv.cvtColor(self.original, cv.COLOR_BGR2GRAY)
        look_up_table = np.empty((1, 256), np.uint8)
        for i in range(256):
            look_up_table[0, i] = np.clip(pow(i / 255.0, self.value["gamma"]) * 255.0, 0, 255)
        image = cv.LUT(image, look_up_table)
        look_up_table = np.empty((1, 256), np.uint8)
        for i in range(256):
            look_up_table[0, i] = np.clip(pow(i / 255.0, self.value["devGamma"]) * 255.0, 0, 255)
        image = cv.LUT(image, look_up_table)

        cv.imwrite(f"resources/{basename(self.value['fileText'])}_{time()}.png", image)


if __name__ == '__main__':
    main = Main()
    main.main()
