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
                print("hoge")
                self.save()

            self.dev_mode_switch()
            # self.dev_slider()
            # self.slider()
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
            [gui.Text(text="シャドー", visible=False),
             gui.Slider(range=(0, 255), default_value=0, size=(40, 15), orientation="h",
                        key="shadow", visible=False)],
            [gui.Text(text="中間調", visible=False),
             gui.Slider(range=(0, 255), default_value=127, size=(40, 15), orientation="h",
                        key="half", visible=False)],
            [gui.Text(text="ハイライト", visible=False),
             gui.Slider(range=(0, 255), default_value=255, size=(40, 15), orientation="h",
                        key="highlight", visible=False)],

            [gui.Checkbox(text="開発者モード", default=False, key="devMode"),
             gui.Button(button_text="セーブ", disabled=True, key="devSave"),
             gui.Button(button_text="ロード", disabled=True, key="devLoad")],
            [gui.Text(text="ガンマ値"),
             gui.Slider(range=(0.0, 10.0), resolution=.05, default_value=self.gamma, disabled=True, size=(40, 15),
                        orientation="h", key="devGamma")],
            [gui.Text(text="シャドー", visible=False),
             gui.Slider(range=(0, 255), default_value=0, disabled=True, size=(40, 15), orientation="h",
                        key="devShadow", visible=False)],
            [gui.Text(text="中間調", visible=False),
             gui.Slider(range=(0, 255), default_value=127, disabled=True, size=(40, 15), orientation="h",
                        key="devHalf", visible=False)],
            [gui.Text(text="ハイライト", visible=False),
             gui.Slider(range=(0, 255), default_value=255, disabled=True, size=(40, 15), orientation="h",
                        key="devHighlight", visible=False)]
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
            self.window["devShadow"].update(disabled=False)
            self.window["devHalf"].update(disabled=False)
            self.window["devHighlight"].update(disabled=False)
        else:
            self.window["devSave"].update(disabled=True)
            self.window["devLoad"].update(disabled=True)
            self.window["devGamma"].update(disabled=True)
            self.window["devShadow"].update(disabled=True)
            self.window["devHalf"].update(disabled=True)
            self.window["devHighlight"].update(disabled=True)

    def dev_slider(self):
        if self.value["devMode"]:
            if self.value["devShadow"] > self.value["devHighlight"]:
                self.window["devShadow"].update(self.value["devHighlight"])
            if self.value["devHalf"] > self.value["devHighlight"]:
                self.window["devHalf"].update(self.value["devHighlight"])
            if self.value["devHalf"] < self.value["devShadow"]:
                self.window["devHalf"].update(self.value["devShadow"])

    def slider(self):
        if self.value["shadow"] > self.value["highlight"]:
            self.window["shadow"].update(self.value["highlight"])
        if self.value["half"] > self.value["highlight"]:
            self.window["half"].update(self.value["highlight"])
        if self.value["half"] < self.value["shadow"]:
            self.window["half"].update(self.value["shadow"])

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
