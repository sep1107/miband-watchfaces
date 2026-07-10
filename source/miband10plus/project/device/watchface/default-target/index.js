try {
  (() => {
    const app = __$$hmAppManager$$__.currentApp;
    const module = app.current;
    const logger = Logger.getLogger('time-flies-band10');

    const SCREEN_WIDTH = 212;
    const SCREEN_HEIGHT = 520;

    let timeSensor;
    let timeText;
    let festivalText;

    function pad2(value) {
      return value < 10 ? `0${value}` : `${value}`;
    }

    function updateTime() {
      if (!timeSensor || !timeText) return;

      const hour = timeSensor.hour;
      const minute = timeSensor.minute;
      timeText.setProperty(hmUI.prop.MORE, {
        text: `${pad2(hour)}:${pad2(minute)}`
      });
    }

    function updateFestival() {
      if (!timeSensor || !festivalText) return;

      const festival = timeSensor.getShowFestival();
      festivalText.setProperty(hmUI.prop.MORE, {
        text: festival === 'INVALID' ? '' : festival
      });
    }

    module.module = DeviceRuntimeCore.WatchFace({
      initView() {
        hmUI.createWidget(hmUI.widget.TEXT, {
          x: 0,
          y: 54,
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
          y: 150,
          w: SCREEN_WIDTH,
          h: 84,
          text: '--:--',
          color: '0xFFFFFFFF',
          text_size: 58,
          align_h: hmUI.align.CENTER_H,
          align_v: hmUI.align.CENTER_V,
          show_level: hmUI.show_level.ONLY_NORMAL
        });

        festivalText = hmUI.createWidget(hmUI.widget.TEXT, {
          x: 24,
          y: 404,
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

        hmUI.createWidget(hmUI.widget.WIDGET_DELEGATE, {
          resume_call() {
            updateTime();
            updateFestival();
          }
        });

        updateTime();
        updateFestival();
      },

      onInit() {
        logger.log(`target canvas ${SCREEN_WIDTH}x${SCREEN_HEIGHT}`);
      },

      build() {
        this.initView();
      },

      onDestroy() {
        logger.log('TIME FLIES watchface destroyed');
      }
    });
  })();
} catch (error) {
  console.log('TIME FLIES watchface error', error);
}
