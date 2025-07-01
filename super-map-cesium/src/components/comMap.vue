<template>
        <div id="cesiumContainer"></div>
</template>

<script>
import Bubble from './bubble/index.js'
import DragEntity from './bubble/dragentity.js'
import WaterLevel from './bubble/waterLevel.js'
export default {
    name: "testMap",
    components: {
    },
    data() {
        return {
            initMap: true,
            poinEntity: [], //地图区域点位集合
            //添加到地图所有的数据集合
            dataSourcesMap: {
                gloab: null,
            },
            gloabMarkeList: [
                {
                    lat: 29.690315741339656,
                    lng: 114.87943613159271,
                    x: -2335079.388078889,
                    y: 5029535.551983973,
                    z: 3141661.647881242,
                    type: 'one',
                    id: '1',
                    name: '富水水库',
                    rainfall: 20,
                    level: 126,//高
                    heading: -60,//角度旋转
                    pitch: -0.1933132632188217,//倾斜角度
                    roll: 0.0,
                    desc: "水库总库容0.4113亿m³，Ⅲ等工程，由主坝、副坝（4座）、溢洪道，输水灌双延满等活筑物组成。设计洪水标准为50年一遇，校核洪水标准为1000年一遇，水库正常落水位70.00m，设计洪水位71.72m，校报洪水位72.59m。"
                },
                {
                    lat: 29.692546735421466,
                    lng: 114.87812723305947,
                    x: -2335079.388078889,
                    y: 5029535.551983973,
                    z: 3141661.647881242,
                    type: 'two',
                    id: '2',
                    name: '富水水库',
                    rainfall: 20,
                    level: 126,//高
                    heading: -60,//角度旋转
                    pitch: -0.1933132632188217,//倾斜角度
                    roll: 0.0,
                    desc: "水库总库容0.4113亿m³，Ⅲ等工程，由主坝、副坝（4座）、溢洪道，输水灌双延满等活筑物组成。设计洪水标准为50年一遇，校核洪水标准为1000年一遇，水库正常落水位70.00m，设计洪水位71.72m，校报洪水位72.59m。"
                },
            ],
        };
    },
    mounted() {
        this.loadMap();
    },
    methods: {
        // 三维
        loadMap() {
            var obj = [6378137.0, 6378137.0, 6356752.3142451793];
            Cesium.Ellipsoid.WGS84 = Object.freeze(
                new Cesium.Ellipsoid(obj[0], obj[1], obj[2])
            );
            window.viewer = new Cesium.Viewer("cesiumContainer", {
                geocoder: false,
                selectionIndicator: false,
                sceneModePicker: true,
                infoBox: false,
                skyAtmosphere: false,
                navigationHelpButton: false,
                navigation: false,
                skyBox: new Cesium.SkyBox({
                    WSpeed: .5,
                    sources: {
                        positiveX: require("../assets/SkyBox/bluesky/Right.jpg"),
                        negativeX: require("../assets/SkyBox/bluesky/Left.jpg"),
                        positiveY: require("../assets/SkyBox/bluesky/Front.jpg"),
                        negativeY: require("../assets/SkyBox/bluesky/Back.jpg"),
                        positiveZ: require("../assets/SkyBox/bluesky/Up.jpg"),
                        negativeZ: require("../assets/SkyBox/bluesky/Down.jpg"),
                    },
                }),
                // 是否显示全屏按钮
                fullscreenButton: false,
                //底部时间轴
                timeline: true,
                animation: false,
            });
            var scene = window.viewer.scene;
            if (this.tabPosition == 1) {
                window.viewer.sceneMode = Cesium.SceneMode.COLUMBUS_VIEW;
            } else {
                window.viewer.sceneMode = Cesium.SceneMode.SCENE3D;
            }
            window.viewer.scene.globe.depthTestAgainstTerrain = true;
            // window.viewer.compass.container.style.display = 'none';
            window.viewer._cesiumWidget._creditContainer.style.display = "none"; //LOGO显示

            var scene = window.viewer.scene;
            var hl = scene.open(
                "http://36.135.21.38:10151/iserver/services/3D-FuShuiSanWeiChangJing/rest/realspace"
            );
            var ditu = scene.open(
                "http://36.135.21.38:10151/iserver/services/3D-fushuiyx/rest/realspace"
            );
            //获取经纬度
            let handler = new Cesium.ScreenSpaceEventHandler(window.viewer.scene.canvas);
            handler.setInputAction(function (event) {
                let cartesian = window.viewer.camera.pickEllipsoid(event.position);
                if (cartesian !== undefined) {
                    let cartographic = Cesium.Cartographic.fromCartesian(cartesian);
                    let lng = Cesium.Math.toDegrees(cartographic.longitude); // 经度
                    let lat = Cesium.Math.toDegrees(cartographic.latitude); // 纬度
                    let height = cartographic.height; // 高度，椭球面height永远等于0
                    let coordinate = {
                        longitude: lng,
                        latitude: lat,
                        height: height,
                    };
                }
                //判断点击的是marker
                let id
                let pick = window.viewer.scene.pick(event.position);
                // console.log('pick')
                // console.log(pick)
                if (Cesium.defined(pick) && (pick.id !== undefined) && (pick.id.id)) {
                    // _this.leftDownFlag = true;
                    id = pick.id.id;
                    let type = pick.id.type;
                    if (id !== undefined) {
                        switch (type) {
                        case 'area':
                            that.bubble(id)
                            break
                        }
                    }
                } else {
                    that.closeAllPopu()
                }

            }, Cesium.ScreenSpaceEventType.LEFT_CLICK);
            let that = this;
            that.addMarker(that.gloabMarkeList)
        },
         //地图上添加区域
         addMarker(pointList) {
            let drag = new DragEntity({
                viewer: window.viewer,
            })
            let drags = new WaterLevel({
                viewer: window.viewer,
            })
            let gloabDataSource = new Cesium.CustomDataSource('gloabEntry')
            let waterLevelSource = new Cesium.CustomDataSource('waterLevel')
            let _this = this
            pointList.forEach(item => {
                let entity = drag.addEntity(item, gloabDataSource);
                _this.poinEntity[item.id] = entity;
            })
            pointList.forEach(item => {
                let temp =  this.formatName(item);
                item.name = temp;
                let entitys = drags.addEntity(item, waterLevelSource);
                _this.poinEntitys[item.id] = entitys;
            })
            this.dataSourcesMap['gloabEntry'] = gloabDataSource
            this.dataSourcesMap['waterLevel'] = waterLevelSource
            window.viewer.dataSources.add(gloabDataSource)
            window.viewer.dataSources.add(waterLevelSource)
        },
         //地图上添加区域
        addMarker(pointList) {
            let drag = new DragEntity({
                viewer: window.viewer,
            })
            let gloabDataSource = new Cesium.CustomDataSource('gloabEntry')
            console.log(gloabDataSource,"gloabEntry")
            let _this = this
            pointList.forEach(item => {
                let entity = drag.addEntity(item, gloabDataSource);
                _this.poinEntity[item.id] = entity;
            })
            this.dataSourcesMap['gloabEntry'] = gloabDataSource
            window.viewer.dataSources.add(gloabDataSource)
        },
         // 格式化数据
         formatName(point){
            if(point.type == 'one'){
                return `水位：${point.level || 0} mm\n雨量：${point.level || 0}mm`
            }else if(point.type == 'two'){
                return `站上水位：${point.level || 0} mm\n站下水位： ${point.level || 0}\n流量： ${point.level || 0}`
            }
        },
        //三点水库弹窗
        bubble(id) {
            if (this.bubbles) {
                this.bubbles.windowClose()
            }
            this.bubbles = new Bubble(Object.assign(this.poinEntity[id], {
                viewer: window.viewer
            }))
        },
        //关闭所有弹框
        closeAllPopu() {
            let that = this
            if (that.bubbles) {
                that.bubbles.windowClose()
            }
        },
    },
};
</script>
<style scoped lang="less">
::v-deep .el-radio__label,
::v-deep .el-checkbox__label {
    color: #fff;
}

#cesiumContainer {
    width: 100%;
    height: calc(100%);
}

.cesium-viewer-bottom {
    display: none !important;
}

.cesium-viewer-navigationContainer {
    display: none !important;
}

.threeSwitch {
    position: fixed;
    top: 90px;
    right: 60px;
}

.fade-enter-active,
.fade-leave-active {
    transition: opacity 2s;
}

.fade-enter,
.fade-leave-to {
    opacity: 0;
}

.header {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 95px;
    display: flex;
    // align-items: center;
    justify-content: center;
    z-index: 1000;
    color: #fff;
    background: url("@/assets/headBg.png") no-repeat center;
    background-size: 100% 100%;

    .headerTitle {
        height: 63px;
        line-height: 63px;
        font-family: AlimamaShuHeiTi;
        font-size: 34px;
        color: #fff;
        line-height: 65px;
        letter-spacing: 3px;
        text-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25);
        text-align: right;
        font-style: normal;
        text-transform: none;
    }

    .components {
        position: fixed !important;
        width: 100px;
        height: 28px;
        top: 10px;
        left: 32px;
        cursor: pointer;
        background: url("@/assets/comBg.png") no-repeat center;
        background-size: 100% 100%;
    }
}

.leftDialog {
    position: fixed;
    top: 80px;
    left: 60px;
    width: 320px;
    height: 800px;
    background: url("@/assets/dialogBg.png") no-repeat center;
    background-size: 100% 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    transition: left 0.8s;

    .closeImg {
        position: absolute;
        top: 13px;
        right: 10px;
        width: 20px;
        height: 20px;
        background: url("@/assets/close.png") no-repeat center;
        background-size: 100% 100%;
        cursor: pointer;

        &:hover {
            background: url("@/assets/close.png") no-repeat center;
            background-size: 100% 100%;
        }
    }

    .headTitle {
        width: 100%;
        height: 33px;
        margin-left: 20px;
        font-size: 20px;
        color: #abdfff;
        line-height: 36px;
        text-align: left;
        font-style: normal;
        text-transform: none;
    }

    .firstBlock {
        margin-top: 20px;
        width: 90%;

        .titleBg {
            background: url("@/assets/titleBg.png") no-repeat center;
            background-size: 100% 100%;
            width: 100%;
            height: 22px;
            font-size: 16px;
            color: #a0f0ff;
            line-height: 20px;
            text-align: left;
            font-style: normal;
            padding-left: 20%;
            box-sizing: border-box;
        }

        .cards {
            margin-top: 16px;
            width: 100%;
            height: auto;
            padding: 5%;
            box-sizing: border-box;
            background: rgba(14, 119, 255, 0.15);

            .weatHead {
                text-align: left;
                margin-bottom: 10px;
                font-size: 14px;
                color: #a0f0ff;
            }
        }
    }
}
</style>