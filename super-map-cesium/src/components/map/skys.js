
/**
 * @param {Viewer} viewer
 * 
*/
// 雾
import FogEffect from './fog'
export default class Sky{
    layers;
    constructor(val) {
        // this.viewer = val.viewer
        // this.scene = viewer.scene
        this.weatherType = val.weatherType
        this.speed = val.speed
        // this.defaultSkyBox = null
        window.blueSkyBox = null;
        window.cloudSkyBox = null;
        window.nightSkyBox = null;
        this.fogs = new FogEffect(window.viewer, {
            visibility: 0.9,
            color: new Cesium.Color(0.8, 0.8, 0.8, 0.9),
            show: true,
        });
        this.layers = window.viewer.scene.layers._layerQueue
        // window.viewer.scene.skyAtmosphere.show = false
    }
    onLoad() {
        console.log('sky-onLoad')
        //创建天空盒
        // var sunSkyBox = new Cesium.SkyBox({
        //     sources:{
        //         positiveX:require('./images/SkyBox/sunsetglow/Right.jpg'),
        //         negativeX:require('./images/SkyBox/sunsetglow/Left.jpg'),
        //         positiveY:require('./images/SkyBox/sunsetglow/Front.jpg'),
        //         negativeY:require('./images/SkyBox/sunsetglow/Back.jpg'),
        //         positiveZ:require('./images/SkyBox/sunsetglow/Up.jpg'),
        //         negativeZ:require('./images/SkyBox/sunsetglow/Down.jpg')
        //     }
        // });
        // window.viewer.scene.debugShowFramesPerSecond = true;
        window.blueSkyBox = new Cesium.SkyBox({
            sources: {
                positiveX: require('./SkyBox/bluesky/Right.jpg'),
                negativeX: require('./SkyBox/bluesky/Left.jpg'),
                positiveY: require('./SkyBox/bluesky/Front.jpg'),
                negativeY: require('./SkyBox/bluesky/Back.jpg'),
                positiveZ: require('./SkyBox/bluesky/Up.jpg'),
                negativeZ: require('./SkyBox/bluesky/Down.jpg')
            }
        });
        window.cloudSkyBox = new Cesium.SkyBox({
            sources: {
                positiveX: require('./SkyBox/cloudy/Right.jpg'),
                negativeX: require('./SkyBox/cloudy/Left.jpg'),
                positiveY: require('./SkyBox/cloudy/Front.jpg'),
                negativeY: require('./SkyBox/cloudy/Back.jpg'),
                positiveZ: require('./SkyBox/cloudy/Up.jpg'),
                negativeZ: require('./SkyBox/cloudy/Down.jpg')
            }
        });
        window.nightSkyBox = new Cesium.SkyBox({
            sources: {
                positiveX: require('./SkyBox/Night/Right.png'),
                negativeX: require('./SkyBox/Night/Left.png'),
                positiveY: require('./SkyBox/Night/Front.png'),
                negativeY: require('./SkyBox/Night/Back.png'),
                positiveZ: require('./SkyBox/Night/Up.png'),
                negativeZ: require('./SkyBox/Night/Down.png')
            }
        });
    }

    //开启天空盒子
    openSkyBox(skyBox) {
        skyBox.WSpeed = 0.5;
        skyBox.show = true;
        let currentSkyBox = skyBox;
        window.viewer.scene.skyBox = skyBox;
        //相机上升到一定位置,天空盒出现渐变效果
        // this.gradualChange(currentSkyBox);

    }
    gradualChange(currentSkyBox) {
        let that = this
        this.skyListener = function () {
            var cameraHeight = window.viewer.scene.camera.positionCartographic.height;
            var skyAtmosphereH1 = 22e4; // 大气开始渐变的最大高度
            var skyBoxH1 = 15e4; // 天空开始渐变的最大高度
            var skyBoxH2 = 12e4; // 天空开始渐变的最小高度
            // var bufferHeight = 1e4;
            var bufferHeight = 1000;
            //相机高度小于大气层高度
            if (cameraHeight < skyAtmosphereH1 && Cesium.defined(currentSkyBox)) {
                var skyAtmosphereT = (cameraHeight - skyBoxH2) / (skyAtmosphereH1 - skyBoxH2);

                if (skyAtmosphereT > 1.0) {
                    skyAtmosphereT = 1.0;
                } else if (skyAtmosphereT < 0.0) {
                    skyAtmosphereT = 0.0;
                }
                var skyBoxT = (cameraHeight - skyBoxH2) / (skyBoxH1 - skyBoxH2);
                if (skyBoxT > 1.0) {
                    skyBoxT = 1.0;
                } else if (skyBoxT < 0.0) {
                    skyBoxT = 0.0;
                }
                currentSkyBox.alpha = 1.0 - skyBoxT;
                if (cameraHeight > skyBoxH2) {
                    window.viewer.scene.skyAtmosphere.show = true;
                    window.viewer.scene.skyAtmosphere.alpha = skyAtmosphereT;
                    window.viewer.scene.skyBox = currentSkyBox;
                } else {
                    window.viewer.scene.skyAtmosphere.show = false;
                }
            } else {
                window.viewer.scene.skyAtmosphere.alpha = 1.0;
                window.viewer.scene.skyBox = that.blueSkyBox;
            }
            //控制相机 速率
            if (window.viewer.scene.skyBox !== that.blueSkyBox) {
                if (cameraHeight > (skyBoxH2 - 2 * bufferHeight) && cameraHeight < skyBoxH1 + 3 * bufferHeight) {
                    window.viewer.scene.screenSpaceCameraController.zoomFactor = 0.4;
                } else {
                    window.viewer.scene.screenSpaceCameraController.zoomFactor = 5.0;
                }
            } else {
                window.viewer.scene.skyBox.alpha = 1.0;
                window.viewer.scene.skyAtmosphere.alpha = 1.0;
                window.viewer.scene.screenSpaceCameraController.zoomFactor = 5.0;
            }

        };
        window.viewer.scene.postRender.addEventListener(that.skyListener);
    }
    //更加类型切换天空盒子
    changeSkyBoxByType(weatherType) {
        switch (weatherType) {
            case 'blueSky':
                window.cloudSkyBox.show = false;
                window.nightSkyBox.show = false;
                window.viewer.scene.postProcessStages.rain.enabled = false
                window.viewer.scene.postProcessStages.snow.enabled = false;
                this.fogs.destroys()
                this.openSkyBox(window.blueSkyBox);
                return
            case 'cloudSky':
                window.blueSkyBox.show = false;
                window.nightSkyBox.show = false;
                window.viewer.scene.postProcessStages.snow.enabled = false;
                this.fogs.destroys()
                this.openSkyBox(window.cloudSkyBox)
                this.rain()
                return
            case 'snowSky':
                window.blueSkyBox.show = false;
                window.nightSkyBox.show = false;
                window.viewer.scene.postProcessStages.rain.enabled = false;
                this.fogs.destroys()
                this.openSkyBox(window.cloudSkyBox)
                this.snow()
                return
            case 'fogSky':
                window.blueSkyBox.show = false;
                window.nightSkyBox.show = false;
                window.viewer.scene.postProcessStages.rain.enabled = false;
                window.viewer.scene.postProcessStages.snow.enabled = false;
                this.openSkyBox(window.cloudSkyBox)
                this.fogs.init()
                return
            case 'nightSky':
                window.viewer.scene.globe.enableLighting = true;
                window.viewer.shadows = true;
                window.viewer.clock.multiplier = 1600;

                window.cloudSkyBox.show = false;
                window.blueSkyBox.show = false;
                window.viewer.scene.postProcessStages.rain.enabled = false;
                window.viewer.scene.postProcessStages.snow.enabled = false;
                this.fogs.destroys()
                this.openSkyBox(window.nightSkyBox)
                return
            case 'null':
                window.cloudSkyBox.show = false;
                window.nightSkyBox.show = false;
                window.viewer.scene.postProcessStages.rain.enabled = false;
                window.viewer.scene.postProcessStages.snow.enabled = false;
                this.fogs.destroys()
                this.openSkyBox(window.blueSkyBox)
                return
        }
    }
    //下雨
    rain() {
        console.log(this.speed, 'this.speed')
        window.viewer.scene.postProcessStages.rain.enabled = true;
        // window.viewer.scene.postProcessStages.rain.uniforms.density = Number(this.speed); 
        window.viewer.scene.postProcessStages.rain.uniforms.angle = 6;  // 角度
        window.viewer.scene.postProcessStages.rain.uniforms.speed = Number(this.speed); //速度
        // console.log(window.viewer.scene.layers._layerQueue,"window.viewer.scene");
        // let layers = this.layers;
        // let groundLayer = layers[2];
        // let buildingLayer = layers[3];
        // groundLayer.style3D.bottomAltitude = 5;
        // Cesium.MemoryManager.setCacheSize(2024);
        // buildingLayer.clearMemoryImmediately = false;

        // groundLayer.setPBRMaterialFromJSON("../json/rain.json");
        // buildingLayer.setPBRMaterialFromJSON("../json/rain.json");
        // let recordRain = 0;
        // let intervalValue = setInterval(() => {
        //     if(groundLayer._PBRMaterialParams.pbrMetallicRoughness.rainEffect !== undefined && buildingLayer._PBRMaterialParams.pbrMetallicRoughness.rainEffect !== undefined) {
        //         if(recordRain === 0) {
        //             groundLayer._PBRMaterialParams.pbrMetallicRoughness.intensityScale = 1.5;
        //             buildingLayer._PBRMaterialParams.pbrMetallicRoughness.intensityScale = 1.5;
        //             layers[0]._PBRMaterialParams.pbrMetallicRoughness.intensityScale = 1.5;
        //             recordRain = 1;
        //         }
        //         groundLayer._PBRMaterialParams.pbrMetallicRoughness.rainEffect.wetnessFactor += 0.0005;
        //         buildingLayer._PBRMaterialParams.pbrMetallicRoughness.rainEffect.wetnessFactor += 0.0005;
        //     }
        //     if(buildingLayer._PBRMaterialParams.pbrMetallicRoughness.rainEffect !== undefined && buildingLayer._PBRMaterialParams.pbrMetallicRoughness.rainEffect.wetnessFactor - 0.85 > 0)
        //         clearInterval(intervalValue);
        // }, 40)
    }
    //下雪
    snow() {
        window.viewer.scene.postProcessStages.snow.enabled = true;
        window.viewer.scene.postProcessStages.snow.uniforms.density = Number(this.speed);  // 密集度
        window.viewer.scene.postProcessStages.snow.uniforms.angle = 6;
        window.viewer.scene.postProcessStages.snow.uniforms.speed = 20;



        // let layers = this.layers;
        // console.log(layers,"layers");
        // let groundLayer = layers[2];
        // let buildingLayer = layers[3];
        // groundLayer.style3D.bottomAltitude = 5;
        // Cesium.MemoryManager.setCacheSize(2024);
        // buildingLayer.clearMemoryImmediately = false;

        // groundLayer.setPBRMaterialFromJSON("../json/snow.json");
        // buildingLayer.setPBRMaterialFromJSON("../json/snow.json");
        // let recordRain = 0;
        // let intervalValue = setInterval(() => {
        //     if(groundLayer._PBRMaterialParams.pbrMetallicRoughness.rainEffect !== undefined && buildingLayer._PBRMaterialParams.pbrMetallicRoughness.rainEffect !== undefined) {
        //         if(recordRain === 0) {
        //             groundLayer._PBRMaterialParams.pbrMetallicRoughness.intensityScale = 1.5;
        //             buildingLayer._PBRMaterialParams.pbrMetallicRoughness.intensityScale = 1.5;
        //             layers[0]._PBRMaterialParams.pbrMetallicRoughness.intensityScale = 1.5;
        //             recordRain = 1;
        //         }
        //         groundLayer._PBRMaterialParams.pbrMetallicRoughness.rainEffect.wetnessFactor += 0.0005;
        //         buildingLayer._PBRMaterialParams.pbrMetallicRoughness.rainEffect.wetnessFactor += 0.0005;
        //     }
        //     if(buildingLayer._PBRMaterialParams.pbrMetallicRoughness.rainEffect !== undefined && buildingLayer._PBRMaterialParams.pbrMetallicRoughness.rainEffect.wetnessFactor - 0.85 > 0)
        //         clearInterval(intervalValue);
        // }, 40)
    }




    
}