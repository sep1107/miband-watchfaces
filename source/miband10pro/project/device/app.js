try {
  (() => {
    const app = __$$hmAppManager$$__.currentApp;

    app.__globals__ = {
      lang: new DeviceRuntimeCore.HmUtils.Lang(
        DeviceRuntimeCore.HmUtils.getLanguage()
      ),
      px: DeviceRuntimeCore.HmUtils.getPx(336)
    };

    app.app = DeviceRuntimeCore.App({
      globalData: {
        model: 'Xiaomi Smart Band 10 Pro',
        canvasWidth: 336,
        canvasHeight: 480,
        targetProfile: 'compat-336x480',
        provisionalTarget: true
      },
      onCreate() {},
      onDestroy() {},
      onError(error) {
        console.log('TIME FLIES Band 10 Pro app error', error);
      }
    });
  })();
} catch (error) {
  console.log('TIME FLIES Band 10 Pro bootstrap error', error);
}
