try {
  (() => {
    const app = __$$hmAppManager$$__.currentApp;
    const module = app.current;
    const logger = Logger.getLogger('time-flies-band10');

    const SCREEN_WIDTH = 212;
    const SCREEN_HEIGHT = 520;

    let timeSensor;
    let stepSensor;
    let heartSensor;
    let batterySensor;

    let timeText;
    let dateText;
    let stepsText;
    let heartText;
    let batteryText;
    let festivalText;

    function pad2(value) {
      const number = Number(value);
      return number < 10 ? `0${number}` : `${number}`;
    }

    function displayNumber(value, fallback = '--') {
      const number = Number(value);
      return Number.isFinite(number) && number >= 0 ? `${number}` : fallback;
    }

    function updateTimeAndDate() {
      if (!timeSensor) return;

      if (timeText) {
        timeText.setProperty(hmUI.prop.MORE, {
          text: `${pad2(timeSensor.hour)}:${pad2(timeSensor.minute)}`
        });
      }

      if (dateText) {
        dateText.setProperty(hmUI.prop.MORE, {
          text: `${timeSensor.year}.${pad2(timeSensor.month)}.${pad2(timeSensor.day)}`
        });
      }
    }

    function updateSteps() {
      if (!stepSensor || !stepsText) return;
      stepsText.setProperty(hmUI.prop.MORE, {
        text: `STEPS ${displayNumber(stepSensor.current, '0')}`
      });
    }

    function updateHeart() {
      if (!heartSensor || !heartText) return;
      heartText.setProperty(hmUI.prop.MORE, {
        text: `HR ${displayNumber(heartSensor.last)}`
      });
    }

    function updateBattery() {
      if (!batterySensor || !batteryText) return;
      batteryText.setProperty(hmUI.prop.MORE, {
        text: `BAT ${displayNumber(batterySensor.current)}%`
      });
    }

    function updateFestival() {
      if (!timeSensor || !festivalText) return;

      const festival = timeSensor.getShowFestival();
      festivalText.setProperty(hmUI.prop.MORE, {
        text: festival === 'INVALID' ? '' : festival
      });
    }

    function refreshAll() {
      updateTimeAndDate();
      updateSteps();
      updateHeart();
      updateBattery();
      updateFestival();
    }

    const minuteListener = function () {
      updateTimeAndDate();
      updateFestival();
    };

    const stepsListener = function () {
      updateSteps();
    };

    const heartListener = function () {
      updateHeart();
    };

    const batteryListener = function () {
      updateBattery();
    };

    module.module = DeviceRuntimeCore.WatchFace({
      initView() {
        hmUI.createWidget(hmUI.widget.FILL_RECT, {
          x: 0,
          y: 0,
          w: SCREEN_WIDTH,
          h: SCREEN_HEIGHT,
          color: '0xFF000000',
          show_level: hmUI.show_level.ONLY_NORMAL
        });

        hmUI.createWidget(hmUI.widget.TEXT, {
          x: 0,
          y: 34,
          w: SCREEN_WIDTH,
          h: 30,
          text: 'TIME FLIES',
          color: '0xFFFFFFFF',
          text_size: 22,
          align_h: hmUI.align.CENTER_H,
          align_v: hmUI.align.CENTER_V,
          show_level: hmUI.show_level.ONLY_NORMAL
        });

        timeText = hmUI.createWidget(hmUI.widget.TEXT, {
          x: 0,
          y: 104,
          w: SCREEN_WIDTH,
          h: 82,
          text: '--:--',
          color: '0xFFFFFFFF',
          text_size: 58,
          align_h: hmUI.align.CENTER_H,
          align_v: hmUI.align.CENTER_V,
          show_level: hmUI.show_level.ONLY_NORMAL
        });

        dateText = hmUI.createWidget(hmUI.widget.TEXT, {
          x: 0,
          y: 194,
          w: SCREEN_WIDTH,
          h: 30,
          text: '----.--.--',
          color: '0xFFB8B8B8',
          text_size: 19,
          align_h: hmUI.align.CENTER_H,
          align_v: hmUI.align.CENTER_V,
          show_level: hmUI.show_level.ONLY_NORMAL
        });

        stepsText = hmUI.createWidget(hmUI.widget.TEXT, {
          x: 16,
          y: 278,
          w: 112,
          h: 28,
          text: 'STEPS 0',
          color: '0xFFFFFFFF',
          text_size: 18,
          align_h: hmUI.align.LEFT,
          align_v: hmUI.align.CENTER_V,
          show_level: hmUI.show_level.ONLY_NORMAL
        });

        heartText = hmUI.createWidget(hmUI.widget.TEXT, {
          x: 128,
          y: 278,
          w: 68,
          h: 28,
          text: 'HR --',
          color: '0xFFFFFFFF',
          text_size: 18,
          align_h: hmUI.align.RIGHT,
          align_v: hmUI.align.CENTER_V,
          show_level: hmUI.show_level.ONLY_NORMAL
        });

        batteryText = hmUI.createWidget(hmUI.widget.TEXT, {
          x: 16,
          y: 330,
          w: 180,
          h: 28,
          text: 'BAT --%',
          color: '0xFFD5D4D4',
          text_size: 18,
          align_h: hmUI.align.CENTER_H,
          align_v: hmUI.align.CENTER_V,
          show_level: hmUI.show_level.ONLY_NORMAL
        });

        festivalText = hmUI.createWidget(hmUI.widget.TEXT, {
          x: 24,
          y: 430,
          w: SCREEN_WIDTH - 48,
          h: 28,
          text: '',
          color: '0xFFD5D4D4',
          text_size: 17,
          align_h: hmUI.align.CENTER_H,
          align_v: hmUI.align.CENTER_V,
          show_level: hmUI.show_level.ONLY_NORMAL
        });

        timeSensor = hmSensor.createSensor(hmSensor.id.TIME);
        stepSensor = hmSensor.createSensor(hmSensor.id.STEP);
        heartSensor = hmSensor.createSensor(hmSensor.id.HEART);
        batterySensor = hmSensor.createSensor(hmSensor.id.BATTERY);

        timeSensor.addEventListener(timeSensor.event.MINUTEEND, minuteListener);
        stepSensor.addEventListener(hmSensor.event.CHANGE, stepsListener);
        heartSensor.addEventListener(heartSensor.event.LAST, heartListener);
        batterySensor.addEventListener(hmSensor.event.CHANGE, batteryListener);

        hmUI.createWidget(hmUI.widget.WIDGET_DELEGATE, {
          resume_call() {
            refreshAll();
          }
        });

        refreshAll();
      },

      onInit() {
        logger.log(`target canvas ${SCREEN_WIDTH}x${SCREEN_HEIGHT}`);
      },

      build() {
        this.initView();
      },

      onDestroy() {
        if (timeSensor) {
          timeSensor.removeEventListener(timeSensor.event.MINUTEEND, minuteListener);
        }
        if (stepSensor) {
          stepSensor.removeEventListener(hmSensor.event.CHANGE, stepsListener);
        }
        if (heartSensor) {
          heartSensor.removeEventListener(heartSensor.event.LAST, heartListener);
        }
        if (batterySensor) {
          batterySensor.removeEventListener(hmSensor.event.CHANGE, batteryListener);
        }
        logger.log('TIME FLIES watchface destroyed');
      }
    });
  })();
} catch (error) {
  console.log('TIME FLIES watchface error', error);
}
