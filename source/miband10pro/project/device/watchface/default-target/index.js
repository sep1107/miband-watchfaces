try {
  (() => {
    const app = __$$hmAppManager$$__.currentApp;
    const module = app.current;
    const logger = Logger.getLogger('time-flies-band10-pro');

    const SCREEN_WIDTH = 400;
    const SCREEN_HEIGHT = 480;
    const SAFE_MARGIN = 24;
    const HEADER_HEIGHT = 58;
    const FOOTER_HEIGHT = 54;
    const LEFT_COLUMN_WIDTH = 238;
    const RIGHT_COLUMN_X = 254;
    const RIGHT_COLUMN_WIDTH = 122;

    let timeSensor;
    let stepSensor;
    let heartSensor;
    let batterySensor;

    let timeText;
    let secondsText;
    let dateText;
    let weekText;
    let stepsText;
    let heartText;
    let batteryText;
    let festivalText;

    function pad2(value) {
      const number = Number(value);
      return number < 10 ? `0${number}` : `${number}`;
    }

    function safeNumber(value, fallback = '--') {
      const number = Number(value);
      return Number.isFinite(number) && number >= 0 ? `${number}` : fallback;
    }

    function weekLabel(week) {
      const labels = ['', 'MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'];
      return labels[Number(week)] || '';
    }

    function setText(widget, text) {
      if (!widget) return;
      widget.setProperty(hmUI.prop.MORE, { text });
    }

    function updateClock() {
      if (!timeSensor) return;
      setText(timeText, `${pad2(timeSensor.hour)}:${pad2(timeSensor.minute)}`);
      setText(secondsText, pad2(timeSensor.second));
      setText(dateText, `${timeSensor.year}.${pad2(timeSensor.month)}.${pad2(timeSensor.day)}`);
      setText(weekText, weekLabel(timeSensor.week));
    }

    function updateSteps() {
      if (!stepSensor) return;
      setText(stepsText, safeNumber(stepSensor.current, '0'));
    }

    function updateHeart() {
      if (!heartSensor) return;
      setText(heartText, safeNumber(heartSensor.last));
    }

    function updateBattery() {
      if (!batterySensor) return;
      setText(batteryText, `${safeNumber(batterySensor.current)}%`);
    }

    function updateFestival() {
      if (!timeSensor) return;
      const festival = timeSensor.getShowFestival();
      setText(festivalText, festival === 'INVALID' ? '' : festival);
    }

    function refreshAll() {
      updateClock();
      updateSteps();
      updateHeart();
      updateBattery();
      updateFestival();
    }

    const minuteListener = function () {
      updateClock();
      updateFestival();
    };
    const stepListener = function () {
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
          x: SAFE_MARGIN,
          y: 16,
          w: SCREEN_WIDTH - SAFE_MARGIN * 2,
          h: 34,
          text: 'TIME FLIES',
          color: '0xFFFFFFFF',
          text_size: 24,
          align_h: hmUI.align.CENTER_H,
          align_v: hmUI.align.CENTER_V,
          show_level: hmUI.show_level.ONLY_NORMAL
        });

        hmUI.createWidget(hmUI.widget.FILL_RECT, {
          x: RIGHT_COLUMN_X - 12,
          y: HEADER_HEIGHT,
          w: 1,
          h: SCREEN_HEIGHT - HEADER_HEIGHT - FOOTER_HEIGHT,
          color: '0xFF333333',
          show_level: hmUI.show_level.ONLY_NORMAL
        });

        timeText = hmUI.createWidget(hmUI.widget.TEXT, {
          x: SAFE_MARGIN,
          y: 118,
          w: LEFT_COLUMN_WIDTH - SAFE_MARGIN,
          h: 100,
          text: '--:--',
          color: '0xFFFFFFFF',
          text_size: 72,
          align_h: hmUI.align.CENTER_H,
          align_v: hmUI.align.CENTER_V,
          show_level: hmUI.show_level.ONLY_NORMAL
        });

        secondsText = hmUI.createWidget(hmUI.widget.TEXT, {
          x: 178,
          y: 212,
          w: 50,
          h: 34,
          text: '--',
          color: '0xFF8B8B8B',
          text_size: 22,
          align_h: hmUI.align.RIGHT,
          align_v: hmUI.align.CENTER_V,
          show_level: hmUI.show_level.ONLY_NORMAL
        });

        dateText = hmUI.createWidget(hmUI.widget.TEXT, {
          x: SAFE_MARGIN,
          y: 262,
          w: LEFT_COLUMN_WIDTH - SAFE_MARGIN,
          h: 32,
          text: '----.--.--',
          color: '0xFFD5D4D4',
          text_size: 21,
          align_h: hmUI.align.CENTER_H,
          align_v: hmUI.align.CENTER_V,
          show_level: hmUI.show_level.ONLY_NORMAL
        });

        weekText = hmUI.createWidget(hmUI.widget.TEXT, {
          x: SAFE_MARGIN,
          y: 302,
          w: LEFT_COLUMN_WIDTH - SAFE_MARGIN,
          h: 28,
          text: '',
          color: '0xFF8B8B8B',
          text_size: 18,
          align_h: hmUI.align.CENTER_H,
          align_v: hmUI.align.CENTER_V,
          show_level: hmUI.show_level.ONLY_NORMAL
        });

        hmUI.createWidget(hmUI.widget.TEXT, {
          x: RIGHT_COLUMN_X,
          y: 90,
          w: RIGHT_COLUMN_WIDTH,
          h: 24,
          text: 'STEPS',
          color: '0xFF777777',
          text_size: 15,
          align_h: hmUI.align.LEFT,
          align_v: hmUI.align.CENTER_V,
          show_level: hmUI.show_level.ONLY_NORMAL
        });
        stepsText = hmUI.createWidget(hmUI.widget.TEXT, {
          x: RIGHT_COLUMN_X,
          y: 116,
          w: RIGHT_COLUMN_WIDTH,
          h: 42,
          text: '0',
          color: '0xFFFFFFFF',
          text_size: 30,
          align_h: hmUI.align.LEFT,
          align_v: hmUI.align.CENTER_V,
          show_level: hmUI.show_level.ONLY_NORMAL
        });

        hmUI.createWidget(hmUI.widget.TEXT, {
          x: RIGHT_COLUMN_X,
          y: 184,
          w: RIGHT_COLUMN_WIDTH,
          h: 24,
          text: 'HEART',
          color: '0xFF777777',
          text_size: 15,
          align_h: hmUI.align.LEFT,
          align_v: hmUI.align.CENTER_V,
          show_level: hmUI.show_level.ONLY_NORMAL
        });
        heartText = hmUI.createWidget(hmUI.widget.TEXT, {
          x: RIGHT_COLUMN_X,
          y: 210,
          w: RIGHT_COLUMN_WIDTH,
          h: 42,
          text: '--',
          color: '0xFFFFFFFF',
          text_size: 30,
          align_h: hmUI.align.LEFT,
          align_v: hmUI.align.CENTER_V,
          show_level: hmUI.show_level.ONLY_NORMAL
        });

        hmUI.createWidget(hmUI.widget.TEXT, {
          x: RIGHT_COLUMN_X,
          y: 278,
          w: RIGHT_COLUMN_WIDTH,
          h: 24,
          text: 'BATTERY',
          color: '0xFF777777',
          text_size: 15,
          align_h: hmUI.align.LEFT,
          align_v: hmUI.align.CENTER_V,
          show_level: hmUI.show_level.ONLY_NORMAL
        });
        batteryText = hmUI.createWidget(hmUI.widget.TEXT, {
          x: RIGHT_COLUMN_X,
          y: 304,
          w: RIGHT_COLUMN_WIDTH,
          h: 42,
          text: '--%',
          color: '0xFFFFFFFF',
          text_size: 30,
          align_h: hmUI.align.LEFT,
          align_v: hmUI.align.CENTER_V,
          show_level: hmUI.show_level.ONLY_NORMAL
        });

        festivalText = hmUI.createWidget(hmUI.widget.TEXT, {
          x: SAFE_MARGIN,
          y: SCREEN_HEIGHT - FOOTER_HEIGHT,
          w: SCREEN_WIDTH - SAFE_MARGIN * 2,
          h: 30,
          text: '',
          color: '0xFFD5D4D4',
          text_size: 18,
          align_h: hmUI.align.CENTER_H,
          align_v: hmUI.align.CENTER_V,
          show_level: hmUI.show_level.ONLY_NORMAL
        });

        timeSensor = hmSensor.createSensor(hmSensor.id.TIME);
        stepSensor = hmSensor.createSensor(hmSensor.id.STEP);
        heartSensor = hmSensor.createSensor(hmSensor.id.HEART);
        batterySensor = hmSensor.createSensor(hmSensor.id.BATTERY);

        timeSensor.addEventListener(timeSensor.event.MINUTEEND, minuteListener);
        stepSensor.addEventListener(hmSensor.event.CHANGE, stepListener);
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
        logger.log(`provisional target canvas ${SCREEN_WIDTH}x${SCREEN_HEIGHT}`);
      },

      build() {
        this.initView();
      },

      onDestroy() {
        if (timeSensor) {
          timeSensor.removeEventListener(timeSensor.event.MINUTEEND, minuteListener);
        }
        if (stepSensor) {
          stepSensor.removeEventListener(hmSensor.event.CHANGE, stepListener);
        }
        if (heartSensor) {
          heartSensor.removeEventListener(heartSensor.event.LAST, heartListener);
        }
        if (batterySensor) {
          batterySensor.removeEventListener(hmSensor.event.CHANGE, batteryListener);
        }
        logger.log('TIME FLIES Band 10 Pro watchface destroyed');
      }
    });
  })();
} catch (error) {
  console.log('TIME FLIES Band 10 Pro watchface error', error);
}
