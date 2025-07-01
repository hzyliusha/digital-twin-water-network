<template>
  <div id="cesiumContainer">
    <!-- <div id="test" class="sm-div-graphic" style="pointer-events: all; display: block; z-index: 9999">
        <div class="divpoint divpoint-theme-29baf1">
            <div class="label-wrap">
                <div class="pop-title">水立方</div>
            </div>
        </div>
    </div> -->
    <div class="infoWindow" v-if="infoState">
      <arxRender ref="ArxChild"/>
    </div>
  </div>
  <!-- <div class="config">
  <span>扩散距离</span><el-slider v-model="distance"></el-slider>
  <span>衰减因子</span><el-slider v-model="dacay"></el-slider>
  <span>光源强度</span><el-slider v-model="intensity"></el-slider>
</div> -->
  <!-- <img src="http://localhost:8099/smoke.png" /> -->
</template>

<script>
import Sky from './map/skys.js';
import Bubble from './bubble/index.js';
import DragEntity from './bubble/dragentity.js';
import WaterLevel from './bubble/waterLevel.js';
import xzhqLine from './../static/xzhq_3d_line.json';
import FloodAnalysis from './cesuims/FloodAnalysis';
import FloodAnalysiss from './cesuims/FloodAnalysiss';
import RealLevel from './cesuims/RealLevel';
import WarningLine from './cesuims/WarningLine';
import WarnLabel from './bubble/warnLabel';
import imge2 from '../assets/image2.png';
import liudong from '../assets/liudong.png';
import weilan from '../assets/weilan.png';
import smoke from '../assets/smoke.png';
import {MapOnlyObjVisible} from './cesuims/OnlyObjsVisible.js';
import DynamicWallMaterialProperty from './cesuims/DynamicWallMaterialProperty.js';
import ws_api from '@/utils/web_socket/ws_api';
import arxRender from '@/components/Arx/arxRender';
// import { computeModelMatrix, computeEmitterModelMatrix, updateCallback } from './cesuims/ParticleSystem.js'
// import * as from './cesuims/polylineTrailLinkMaterialProperty.js'
let flyManager = null;//漫游
export default {
  name: 'testMap',
  components: {
    arxRender
  },
  data() {
    var start = new Date();
    var stop = new Date().getTime() + 24 * 60 * 60 * 1000;
    const viewer = null;
    return {
      weather: 1,
      checkList: [1, 2, 3],
      isHide: false,
      skyObj: null, //天空对象
      submergeA: null, //淹没分析的对象
      fooldingA: null, //连通性分析的对象
      weatherType: 'blueSky',
      initMap: true, //是否是初始化地图
      poinEntity: [], //地图区域点位集合
      poinEntitys: [], //地图区域点位集合
      siteEntity: [], //点位集合
      szyEntity: [], // d水资源点位集合
      pqPoinEntity: [], //片区的点位集合
      //添加到地图所有的数据集合
      dataSourcesMap: {
        gloab: null
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
          level: 126, //高
          heading: -60, //角度旋转
          pitch: -0.1933132632188217, //倾斜角度
          roll: 0.0,
          desc: '水库总库容0.4113亿m³，Ⅲ等工程，由主坝、副坝（4座）、溢洪道，输水灌双延满等活筑物组成。设计洪水标准为50年一遇，校核洪水标准为1000年一遇，水库正常落水位70.00m，设计洪水位71.72m，校报洪水位72.59m。'
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
          level: 126, //高
          heading: -60, //角度旋转
          pitch: -0.1933132632188217, //倾斜角度
          roll: 0.0,
          desc: '水库总库容0.4113亿m³，Ⅲ等工程，由主坝、副坝（4座）、溢洪道，输水灌双延满等活筑物组成。设计洪水标准为50年一遇，校核洪水标准为1000年一遇，水库正常落水位70.00m，设计洪水位71.72m，校报洪水位72.59m。'
        }
      ],
      floodPlayData: {
        startTime: start,
        endTime: new Date(stop),
        minIndex: 1,
        maxIndex: 150,
        dataList: [
          {
            time: '2024-07-25 08:00:00',
            sw: 1.0
          },
          {
            time: '2024-07-25 09:00:00',
            sw: 2.27
          },
          {
            time: '2024-07-25 10:00:00',
            sw: 3.39
          },
          {
            time: '2024-07-25 11:00:00',
            sw: 4.7
          },
          {
            time: '2024-07-25 12:00:00',
            sw: 5.25
          },
          {
            time: '2024-07-25 13:00:00',
            sw: 6.5
          },
          {
            time: '2024-07-25 14:00:00',
            sw: 7.75
          },
          {
            time: '2024-07-25 15:00:00',
            sw: 8.0
          },
          {
            time: '2024-07-25 16:00:00',
            sw: 9.25
          },
          {
            time: '2024-07-25 17:00:00',
            sw: 10.5
          },
          {
            time: '2024-07-25 18:00:00',
            sw: 11.75
          },
          {
            time: '2024-07-25 19:00:00',
            sw: 12.0
          },
          {
            time: '2024-07-25 20:00:00',
            sw: 13.25
          },
          {
            time: '2024-07-25 21:00:00',
            sw: 14.5
          },
          {
            time: '2024-07-25 22:00:00',
            sw: 15.75
          },
          {
            time: '2024-07-25 23:00:00',
            sw: 16.0
          },
          {
            time: '2024-07-26 00:00:00',
            sw: 26.25
          },
          {
            time: '2024-07-26 01:00:00',
            sw: 27.5
          },
          {
            time: '2024-07-26 02:00:00',
            sw: 28.75
          },
          {
            time: '2024-07-26 03:00:00',
            sw: 29.0
          },
          {
            time: '2024-07-26 04:00:00',
            sw: 30.25
          },
          {
            time: '2024-07-26 05:00:00',
            sw: 31.5
          },
          {
            time: '2024-07-26 06:00:00',
            sw: 32.75
          },
          {
            time: '2024-07-26 07:00:00',
            sw: 33.0
          }
        ]
      },
      submergeA: null, //淹没分析的对象
      fogs: null,
      waterTimer: null,
      waterEntity: null, //水体流动
      waterEntityRiver: null,
      layerS3M: null,
      //河流面Geojson
      PolygonGeoJson: [
        114.88584997638775, 29.68839993842363, 20, 114.88614935481371, 29.688486527355586, 20, 114.88651792701451, 29.688570673855036, 20, 114.88735184751332, 29.688870160811035, 20, 114.88801541744932, 29.689134838842623, 20, 114.88823819004057, 29.689275166957156, 20, 114.88876756846811, 29.6894328289383, 20, 114.88923085417622, 29.68963556341666, 20, 114.88955501221305, 29.68987864678659, 20, 114.8900351727296, 29.69026025609593, 20, 114.89038585940753, 29.690708240951608, 20,
        114.89075018261202, 29.690987617275113, 20, 114.89082240955312, 29.69161753317734, 20, 114.89082869932331, 29.692191288205443, 20, 114.88958303908284, 29.69262285575298, 20, 114.88932236646447, 29.691952628056438, 20, 114.88902902671984, 29.69148075000074, 20, 114.88847285223682, 29.69111832614291, 20, 114.88788938946384, 29.69078914411543, 20, 114.88782953896389, 29.690706041426996, 20, 114.88759363338049, 29.690412819435938, 20, 114.88693063956235, 29.69009487524241, 20,
        114.8860592025517, 29.689785510379057, 20, 114.88543335587904, 29.68956836064428, 20
      ],
      //河流线Geojson
      polylineGeoJson: [114.88569927987122, 29.68904678518808, 114.88596838338367, 29.689121385329997, 114.88623279536746, 29.68921557928587, 114.88663347398028, 29.68940106121591, 114.88725690474193, 29.689612302603642, 114.88758952446913, 29.689739359173103, 114.88798428401198, 29.689949299043473, 114.88824346493901, 29.690114086035447],
      viewer: null,
      WallLineJson: [
        114.8322983314873, 29.671710245649184, 114.83672677142746, 29.668446883870917, 114.84362349107404, 29.668553627655974, 114.85047815664556, 29.66921164004471, 114.86084088388205, 29.670854406897703, 114.86677665540684, 29.6718167707358, 114.88120682899755, 29.67643031303753, 114.89610990629554, 29.687652704096667, 114.8997824355428, 29.69389329993171, 114.90048382255345, 29.69944154402559, 114.8945115709124, 29.70734365551872, 114.86859277070617, 29.70500276813967,
        114.84374780802797, 29.694929589552828, 114.8348141543196, 29.691152543341044, 114.82442203269993, 29.691331751762693, 114.82154114077083, 29.673757967753183, 114.82160702562987, 29.668731810522214, 114.8322983314873, 29.671710245649184
      ],
      ett: null, //实体围栏
      inter: null, //光照定时器
      pointEntity: null, //光源实体
      pointLightTest: null, //光源
      infoState: false, //气泡
      // distance: 1000,//扩散距离0-2000
      // dacay: 1,//衰减因子  1-100
      // intensity: 7,//光源强度  0-20
    };
  },
  created() {
    localStorage.setItem('initMap', true);
  },
  mounted() {
    // let textStyle = {
    //     text: '实时水面高度: 50',
    //     fontSize: 24,
    //     color: "#000",
    // }
    // this.createdText(textStyle)
    this.loadMap();
    this.$bus.on('skyChange', val => {
      this.skyChanges(val);
    }),
        this.$bus.on('drawWaterClick', val => {
          if (val) {
            this.drawWater();
          } else {
            if (this.waterTimer) {
              clearInterval(this.waterTimer);
            }
            window.viewer.entities.remove(this.waterEntity);
            window.viewer.entities.remove(this.waterEntityRiver);
          }
        }),
        this.$bus.on('GameEngine', val => {
          if (val) {
            this.infoState = val;
          } else {
            ws_api.disconnectArxServer();
            this.infoState = val;
            // disconnectArxServer
          }
        }),
        //水库漫游
        this.$bus.on('Roam', val => {
          if (val) {
            this.flyRoute();
          } else {
            flyManager && flyManager.stop();
            flyManager = null;
          }
        });
    // 淹没效果
    this.$bus.on('floodChange', val => {
      if (val.length > 0) {
        let fllodJSON = require('./cesuims/flood.json');
        if (this.floodPlayData && this.floodPlayData.dataList.length > 0) {
          let start = this.floodPlayData.dataList[0].time;
          let startTime = new Date(start);
          let end = this.floodPlayData.dataList[this.floodPlayData.dataList.length - 1].time;
          let endTime = new Date(end);
          this.floodPlayData.startTime = startTime;
          this.floodPlayData.endTime = endTime;
          let diff = this.floodPlayData.maxIndex - this.floodPlayData.minIndex;
          let steep = diff / this.floodPlayData.dataList.length;
          let cx = 0;
          this.floodPlayData.dataList.forEach(item => {
            let sw = item.rz == null || item.rz == '' ? 12 : item.rz;
            // item.sw = parseFloat(sw)
            item.sw = this.floodPlayData.minIndex + steep * cx;
            cx++;
          });
          // console.log(this.floodPlayData.dataList,"this.floodPlayData.dataList")
          // this.floodPlayData.dataList = fllodJSON
          this.floodAnalyse(this.floodPlayData);
        }
      } else {
        if (window.submergeA) {
          window.submergeA.destroy();
          // window.submergeA.clearSubmerge('Combine_10')
          window.submergeA = undefined;
        }
      }
    }),
        this.$bus.on('PointLight', val => {
          if (val) {
            this.PointLight();
          } else {
            let scene = window.viewer.scene;
            scene.removeLightSource(this.pointLightTest);
            window.viewer.entities.remove(this.pointEntity);
          }
        }),
        this.$bus.on('polylineGlowClick', val => {
          if (val) {
            this.polylineGlow();
          } else {
            window.viewer.entities.remove(this.ett);
          }
        }),
        this.$bus.on('kArrChange', val => {
          if (!val.length) return;
          // 相机的位置
          var initialPosition = new Cesium.Cartesian3(-2333775.0514087607, 5030460.1841748655, 3140576.87666044);
          // 视角
          var orientation = {
            heading: 4.4015566947406795,
            pitch: -0.19314376301249592,
            roll: 0.000001134507515487826
          };
          var homeCameraView = {
            destination: initialPosition, // 相机的位置
            orientation: orientation
          };
          //设置默认角度
          window.viewer.scene.camera.flyTo(homeCameraView);
        }),
        // 水库水位高度
        this.$bus.on('waterZ', val => {
          console.log(this.dataSourcesMap['realEntry'], '=============================');
          //&& this.dataSourcesMap['labelDialog'] != undefined
          if (this.dataSourcesMap['realEntry'] != undefined) {
            window.viewer.dataSources.remove(this.dataSourcesMap['realEntry']);
            // window.viewer.dataSources.remove(this.dataSourcesMap['labelDialog']);
          }
          let waterHeight = window.viewer.scene.layers.find('bt_surface_3D@water');
          waterHeight.style3D.bottomAltitude = val - 50;
          // dataSource.entities.removeAll();
          // viewer.dataSources.remove(realsDataSource);
          let realsDataSource = new Cesium.CustomDataSource('realEntry');
          let realTime = new RealLevel();
          realTime._initWater(realsDataSource, val);
          this.dataSourcesMap['realEntry'] = realsDataSource;
          window.viewer.dataSources.add(realsDataSource);
        });
    this.$bus.on('MachineryClick', val => {
      //显示内部电机
      // console.log(val, "电机")
      if (val) {
        var initialPosition = new Cesium.Cartesian3(-2333711.081395686, 5030527.729373825, 3140550.123045529); // 相机的位置
        var orientation = {
          // 视角
          heading: 4.510758281662342,
          pitch: -0.1930136568284042,
          roll: 0.000001178976492433037
        };
        var homeCameraView = {
          destination: initialPosition, // 相机的位置
          orientation: orientation
        };
        //设置默认角度
        window.viewer.scene.camera.flyTo(homeCameraView);
      }
      MapOnlyObjVisible(window.viewer.scene, 'fushuishuiku_adjust@DataSourceNew', ['79', '73', '80', '77', '78', '74'], !val);
      // let selectlayer = window.viewer.scene.layers.find("fushuishuiku_adjust@DataSourceNew")
      let list = ['79', '73', '80', '77', '78', '74'];
      // selectlayer.setOnlyObjsVisible(list, !val)
    });
    this.$bus.on('DamClick', val => {
      if (val) {
        var initialPosition = new Cesium.Cartesian3(-2333763.063808348, 5030563.030623509, 3141672.4559321334); // 相机的位置
        var orientation = {
          // 视角
          heading: 3.734516778842926,
          pitch: -0.7537679999069238,
          roll: 0.000004462558017337415
        };
        var homeCameraView = {
          destination: initialPosition, // 相机的位置
          orientation: orientation
        };
        //设置默认角度
        window.viewer.scene.camera.flyTo(homeCameraView);
      }
      //显示河坝内部构造
      MapOnlyObjVisible(window.viewer.scene, 'fushuishuiku_adjust@DataSourceNew', ['32', '14'], !val);
    });
    // 警戒线
    this.$bus.on('warnLine', val => {
      let warningLine = new WarningLine(window.viewer);
      if (!val.length) {
        warningLine.removeLine();
        window.viewer.dataSources.remove(this.dataSourcesMap['labelDialog']);
      } else {
        var initialPosition = new Cesium.Cartesian3(-2335711.621783721, 5029088.192067285, 3141791.6758792405); // 相机的位置
        var orientation = {
          // 视角
          heading: 4.692990032610092,
          pitch: -0.42372277073206654,
          roll: 2.6191272617381856e-7
        };
        var homeCameraView = {
          destination: initialPosition, // 相机的位置
          orientation: orientation
        };
        //设置默认角度
        window.viewer.scene.camera.flyTo(homeCameraView);
        let position = [114.90418014179835, 29.699969037277853, 30, 114.90416393389663, 29.701312463044424, 30];
        warningLine._initWarningLine(position);
        let labels = new WarnLabel();
        let labelSource = new Cesium.CustomDataSource('labelDialog');
        let _this = this;
        let obj = {
          names: '警戒水位高度50米',
          id: 'warnHeight',
          lng: 114.90424728395797,
          lat: 29.70058330458311,
          height: 30
        };
        labels.addEntity(obj, labelSource);
        _this.dataSourcesMap['labelDialog'] = labelSource;
        window.viewer.dataSources.add(labelSource);
      }
    });
    window.addEventListener('beforeunload', this.handleBeforeUnload);
    window.addEventListener('unload', this.handleUnload);
  },
  watch: {
    weather: {
      handler: function (val) {
      }
    }
  },
  methods: {
    loadMapTest() {
      let mapOption = {
        //地图可进行切换
        //高德影像地图
        //url:"https://webst04.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}",
        //google地图（国内暂时被封），后续如果开放可直接f12-->network获取服务
        //osm矢量地图
        //url:"https://b.tile.openstreetmap.org/{z}/{x}/{y}.png",
        //mapbox影像地图(token如果过期，请选择其他地图图层)
        //url:"https://api.mapbox.com/styles/v1/marsgis/cki0adkar2b0e19mv9tpiewld/tiles/512/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoibWFyc2dpcyIsImEiOiJja2Fod2xlanIwNjJzMnhvMXBkMnNqcjVpIn0.WnxikCaN2KV_zn9tLZO77A"
        //arcgis影像地图
        url: 'https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
      };
      let imgProvider = new Cesium.UrlTemplateImageryProvider(mapOption);
      let viewerOption = {
        animation: false, //是否创建动画小器件，左下角仪表
        baseLayerPicker: false, //是否显示图层选择器
        fullscreenButton: false, //是否显示全屏按钮
        geocoder: false, //是否显示geocoder小器件，右上角查询按钮
        homeButton: false, //是否显示Home按钮
        infoBox: false, //是否显示信息框
        sceneModePicker: false, //是否显示3D/2D选择器
        scene3DOnly: false, //如果设置为true，则所有几何图形以3D模式绘制以节约GPU资源
        selectionIndicator: false, //是否显示选取指示器组件
        timeline: true, //是否显示时间轴
        navigationHelpButton: false, //是否显示右上角的帮助按钮
        baselLayerPicker: false, // 将图层选择的控件关掉，才能添加其他影像数据
        shadows: true, //是否显示背影
        shouldAnimate: true,
        imageryProvider: imgProvider
        //加载地形
        // terrainProvider: new Cesium.CesiumTerrainProvider({
        //     url: "http://data.marsgis.cn/terrain",
        // })
      };
      // 创建一个Viewer实例
      this.viewer = new Cesium.Viewer('cesiumContainer', viewerOption);
      let scene = this.viewer.scene;
      // scene.lightSource.ambientLightColor = new Cesium.Color(0.65, 0.65, 0.65, 1);
      // scene.debugShowFramesPerSecond = true;
      // if (this.tabPosition == 1) {
      //     window.viewer.sceneMode = Cesium.SceneMode.COLUMBUS_VIEW;
      // } else {
      //     window.viewer.sceneMode = Cesium.SceneMode.SCENE3D;
      // }
      scene.globe.depthTestAgainstTerrain = true;
      // window.viewer.compass.container.style.display = 'none';
      this.viewer._cesiumWidget._creditContainer.style.display = 'none'; //LOGO显示
      // document.getElementsByClassName('cesium-viewer-animationContainer')[0].setAttribute('style', 'display: none;')
      // document.getElementsByClassName('cesium-viewer-timelineContainer')[0].setAttribute('style', 'display: none;')
      // var scene = window.viewer.scene;
      var hl = scene.open('http://36.135.21.38:10151/iserver/services/3D-FuShuiSanWeiChangJing/rest/realspace');
      var ditu = scene.open('http://36.135.21.38:10151/iserver/services/3D-fushuiyx/rest/realspace');
      this.viewer.scene.debugShowFramesPerSecond = true;
      this.$bus.emit('zhjc', true);
    },
    // 三维
    loadMap() {
      var obj = [6378137.0, 6378137.0, 6356752.3142451793];
      Cesium.Ellipsoid.WGS84 = Object.freeze(new Cesium.Ellipsoid(obj[0], obj[1], obj[2]));
      window.viewer = new Cesium.Viewer('cesiumContainer', {
        // terrainProvider: new Cesium.EllipsoidTerrainProvider(),
        // terrainProvider: new Cesium.CesiumTerrainProvider({
        //     url: 'URL_CONFIG.ZF_TERRAIN',
        //     isSct: true//地形服务源自SuperMap iServer发布时需设置isSct为true
        // }),
        geocoder: false,
        selectionIndicator: false,
        sceneModePicker: false,
        infoBox: false,
        skyAtmosphere: false,
        navigationHelpButton: false,
        navigation: false,
        shouldAnimate: true,
        skyBox: new Cesium.SkyBox({
          WSpeed: 0.5,
          sources: {
            positiveX: require('./map/SkyBox/bluesky/Right.jpg'),
            negativeX: require('./map/SkyBox/bluesky/Left.jpg'),
            positiveY: require('./map/SkyBox/bluesky/Front.jpg'),
            negativeY: require('./map/SkyBox/bluesky/Back.jpg'),
            positiveZ: require('./map/SkyBox/bluesky/Up.jpg'),
            negativeZ: require('./map/SkyBox/bluesky/Down.jpg')
          }
        }),
        terrainProvider: Cesium.createWorldTerrain({
          requestVertexNormals: true,
          requestWaterMask: true
        }),
        // 是否显示全屏按钮
        fullscreenButton: false,
        //底部时间轴
        timeline: true,
        animation: true
      });
      var scene = window.viewer.scene;
      // scene.lightSource.ambientLightColor = new Cesium.Color(0.65, 0.65, 0.65, 1);
      // scene.debugShowFramesPerSecond = true;
      // if (this.tabPosition == 1) {
      //     window.viewer.sceneMode = Cesium.SceneMode.COLUMBUS_VIEW;
      // } else {
      //     window.viewer.sceneMode = Cesium.SceneMode.SCENE3D;
      // }
      scene.globe.depthTestAgainstTerrain = true;
      // window.viewer.compass.container.style.display = 'none';
      window.viewer._cesiumWidget._creditContainer.style.display = 'none'; //LOGO显示
      document.getElementsByClassName('cesium-viewer-animationContainer')[0].setAttribute('style', 'display: none;');
      document.getElementsByClassName('cesium-viewer-timelineContainer')[0].setAttribute('style', 'display: none;');
      // var scene = window.viewer.scene;
      var hl = scene.open('http://36.135.21.38:10151/iserver/services/3D-FuShuiSanWeiChangJing/rest/realspace');
      var ditu = scene.open('http://36.135.21.38:10151/iserver/services/3D-fushuiyx/rest/realspace');
      Cesium.Timeline.prototype.makeLabel = this.CesiumDateTimeFormatter;
      // window.viewer.animation.viewModel.dateFormatter = this.CesiumDateFormatter;
      // window.viewer.animation.viewModel.timeFormatter = this.CesiumTimeFormatter;
      var style = new Cesium.Style3D();
      style.bottomAltitude = -1000;
      hl.style3D = style;
      window.viewer.scene.globe.depthTestAgainstTerrain = false;
      // window.viewer.imageryLayers.addImageryProvider(
      //     new Cesium.ArcGisMapServerImageryProvider({
      //         url: "https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer",
      //     })
      // );

      hl.then(function (layers) {
        this.openSky(scene);
      });
      Cesium.when(hl, function (layers) {
        layerS3M = layers[0];
      });
      //创建气泡
      //1.固定显示弹框
      // this.popup = new Popup({
      //     viewer: window.viewer,
      //     element: document.getElementById('test'),
      //     show: true,
      //     position: {
      //         x: -2334064.7674551876,
      //         y: 5030135.8400643915,
      //         z: 3141924.9882809375
      //     },
      //     pixelOffset: new Cesium.Cartesian2(-64, -216),
      //     scaleByDistance: new Cesium.NearFarScalar(1000, 1, 10000, 0.2),
      //     distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0, 11000)
      // });

      //获取经纬度
      let handler = new Cesium.ScreenSpaceEventHandler(window.viewer.scene.canvas);
      handler.setInputAction(function (event) {
        // let selectlayer = window.viewer.scene.layers.getSelectedLayer()
        // let selectid = selectlayer.getSelection()[0];
        // // selectlayer.setOnlyObjsVisible(selectid, false)
        // console.log(selectlayer);//[79,73,80,77,78,74];[31]
        // console.log(selectid);

        let cartesian = window.viewer.camera.pickEllipsoid(event.position);
        console.log(cartesian);
        console.log(event.position);
        if (cartesian !== undefined) {
          let cartographic = Cesium.Cartographic.fromCartesian(cartesian);
          let lng = Cesium.Math.toDegrees(cartographic.longitude); // 经度
          let lat = Cesium.Math.toDegrees(cartographic.latitude); // 纬度
          console.log(Cesium.Cartesian3.fromDegrees(lng, lat, 300));
          console.log(lng + '|' + cartographic.longitude + ',' + cartographic.latitude + '|' + lat);
          let height = cartographic.height; // 高度，椭球面height永远等于0
          let height2 = window.viewer.scene.globe.getHeight(cartographic);
          let coordinate = {
            longitude: lng,
            latitude: lat,
            height: height,
            height2: height2
          };
          //   that.$bus.emit("showLng", coordinate);
          console.log('==========位置信息==============');
          console.log(coordinate);
        }
        // console.log("==========相机位置==============");
        console.log(window.viewer.scene.camera.heading);
        console.log(window.viewer.scene.camera.pitch);
        console.log(window.viewer.scene.camera.roll);
        console.log(window.viewer.scene.camera.position);

        //判断点击的是marker
        let id;
        let pick = window.viewer.scene.pick(event.position);
        // console.log(viewer.scene.layers, "layerQueue")
        // that.Popupposition(event)
        if (Cesium.defined(pick) && pick.id !== undefined && pick.id.id) {
          // _this.leftDownFlag = true;
          id = pick.id.id;
          let type = pick.id.type;
          if (id !== undefined) {
            switch (type) {
              case 'area':
                that.bubble(id);
                break;
            }
          }
        } else {
          that.closeAllPopu();
        }
      }, Cesium.ScreenSpaceEventType.LEFT_CLICK);

      // var initialPosition = new Cesium.Cartesian3(
      //     -2335079.3880788814,
      //     5029535.551983976,
      //     3141661.6478812424
      // ); // 相机的位置

      // //监听地图是否渲染完毕
      let that = this;
      let index = 2;
      let i = 1;
      var helper = new Cesium.EventHelper();
      setTimeout(() => {
        // 相机的位置
        var initialPosition = new Cesium.Cartesian3(-2334064.7674551876, 5030135.8400643915, 3141924.9882809375);
        var orientation = {
          heading: 3.885880545101143,
          // 视角
          pitch: -0.3652049044617751,
          roll: 2.950761528452972e-7
        };
        var homeCameraView = {
          destination: initialPosition, // 相机的位置
          orientation: orientation
        };
        window.viewer.scene.camera.setView(homeCameraView);
        that.$bus.emit('zhjc', true);
      }, 10000);
      helper.add(window.viewer.scene.globe.tileLoadProgressEvent, function (event) {
        if (event == 0 && that.initMap) {
          // 全流域
          // var initialPosition = new Cesium.Cartesian3(
          //     -2398310.431982037,
          //     5060823.4448838895,
          //     3158623.4442337574
          // ); // 相机的位置
          // var orientation = {
          //     heading: 5.59865731167752,
          //     // 视角
          //     pitch: -1.047594790118275,
          //     roll: 6.283182648700873,
          // };
          // 库区
          // var initialPosition = new Cesium.Cartesian3(
          //     -2359428.9677469973,
          //     5063708.78351821,
          //     3146073.290586828
          // ); // 相机的位置
          // var orientation = {
          //     heading: 5.595442536960972,
          //     // 视角
          //     pitch: -1.04605441738638,
          //     roll: 6.283181521492734,
          // };
          // 大坝下游
          // var initialPosition = new Cesium.Cartesian3(
          //     -2409364.113922912,
          //     5045883.120785395,
          //     3162665.216875195
          // ); // 相机的位置
          // var orientation = {
          //     heading: 5.600108107133631,
          //     // 视角
          //     pitch: -1.0471021771538616,
          //     roll: 0.0000017119227626594125,
          // };
          // 相机的位置
          var initialPosition = new Cesium.Cartesian3(-2334064.7674551876, 5030135.8400643915, 3141924.9882809375);
          var orientation = {
            heading: 3.885880545101143,
            // 视角
            pitch: -0.3652049044617751,
            roll: 2.950761528452972e-7
          };
          var homeCameraView = {
            destination: initialPosition, // 相机的位置
            orientation: orientation
          };
          if (i == 1) {
            console.log('定位视角', homeCameraView);
            //设置默认角度
            window.viewer.scene.camera.setView(homeCameraView);
            that.$bus.emit('zhjc', true);
          }
          if (i == index) {
            i = 1;
            that.initMap = false;
            localStorage.setItem('initMap', false);
            console.log('发送通知-地图初始化完成');
            window.viewer.scene.camera.setView(homeCameraView);
            //地图初始化完成，通知综合检测可以进行地图操作了
            that.$bus.emit('zhjc', true);
            const position = {
              x: 114.88565560050606,
              y: 29.688334699279462,
              z: 100.0
            };

            // that.updateWaterZ();
          }
          i++;
        }
      });
      // window.viewer.scene.camera.setView(homeCameraView);
      that.addMarker(that.gloabMarkeList);

      // that.$bus.on('pcZHJCCreatMarker', (val) => {
      //     // console.log(val,'接收通知-扎点-全局三点')

      // })
    },

    flyRoute() {
      let routes = new Cesium.RouteCollection(window.viewer.entities);
      //添加fpf飞行文件，fpf由SuperMap iDesktop生成
      let fpfUrl = './flyFiles/fushui.fpf';
      // console.log(fushuifpf);
      routes.fromFile(fpfUrl);
      //初始化飞行管理
      flyManager = new Cesium.FlyManager({
        scene: window.viewer.scene,
        routes: routes
      });
      //注册站点到达事件
      flyManager.stopArrived.addEventListener(function (routeStop) {
        routeStop.waitTime = 1; // 在每个站点处停留1s
      });
      flyManager.readyPromise.then(function () {
        let currentRoute = flyManager.currentRoute;
        currentRoute.isLineVisible = false;
        currentRoute.isStopVisible = false;
      });
      setTimeout(() => {
        flyManager.currentRoute.isLineVisible = false;
        flyManager.currentRoute.isStopVisible = false;
        flyManager && flyManager.play();
      }, 2000);
    },
    // 创建文字画布
    createdText(obj) {
      const text = obj.text;
      var textCanvas = document.createElement('canvas');
      const width = text.length * obj.fontSize;
      textCanvas.width = width;
      textCanvas.height = 36;
      var ctx = textCanvas.getContext('2d');
      ctx.fillStyle = obj.color;
      ctx.font = 'bold ' + obj.fontSize + 'px 微软雅黑'; //设置字体
      ctx.textBaseline = 'hanging'; //在绘制文本时使用的当前文本基线
      //绘制文本
      ctx.fillText(text, 0, 0);
      let image = new Image();
      image.src = textCanvas.toDataURL('image/png');
      return textCanvas.toDataURL('image/png');
    },

    //开启天空--影响三维图颜色
    openSky(scene) {
      let that = this;
      that.skyObj = new Sky({
        weatherType: that.weatherType
      });
      that.skyObj.onLoad();
    },
    // 天气变化
    skyChanges(weatherType) {
      let that = this;
      console.log(weatherType.split('-'), '=============');

      that.weatherType = weatherType.split('-')[0];
      if (weatherType.split('-').length == 2) {
        that.skyObj = new Sky({
          weatherType: that.weatherType,
          speed: weatherType.split('-')[1]
        });
      } else {
        that.weatherType = weatherType;
        that.skyObj = new Sky({
          weatherType: that.weatherType,
          speed: 0
        });
      }
      that.skyObj.onLoad();
      that.skyObj.changeSkyBoxByType(that.weatherType);
    },
    // cesium时钟时间格式化函数
    CesiumTimeFormatter(datetime, viewModel) {
      var julianDT = new Cesium.JulianDate();
      Cesium.JulianDate.addHours(datetime, 8, julianDT);
      var gregorianDT = Cesium.JulianDate.toGregorianDate(julianDT);

      let hour = gregorianDT.hour + '';
      let minute = gregorianDT.minute + '';
      let second = gregorianDT.second + '';
      return `${hour.padStart(2, '0')}:${minute.padStart(2, '0')}:${second.padStart(2, '0')}`;
    },
    // cesium时钟日期格式化函数
    CesiumDateFormatter(datetime, viewModel, ignoredate) {
      var julianDT = new Cesium.JulianDate();
      Cesium.JulianDate.addHours(datetime, 8, julianDT);
      var gregorianDT = Cesium.JulianDate.toGregorianDate(julianDT);

      return `${gregorianDT.year}年${gregorianDT.month}月${gregorianDT.day}日`;
    },
    // cesium时间轴格式化函数
    CesiumDateTimeFormatter(datetime, viewModel, ignoredate) {
      var julianDT = new Cesium.JulianDate();
      Cesium.JulianDate.addHours(datetime, 8, julianDT);
      var gregorianDT = Cesium.JulianDate.toGregorianDate(julianDT);

      let hour = gregorianDT.hour + '';
      let minute = gregorianDT.minute + '';
      return `${gregorianDT.day}日${hour.padStart(2, '0')}时`;
    },
    //地图上添加区域
    addMarker(pointList) {
      let drag = new DragEntity({
        viewer: window.viewer
      });
      let drags = new WaterLevel({
        viewer: window.viewer
      });
      let gloabDataSource = new Cesium.CustomDataSource('gloabEntry');
      let waterLevelSource = new Cesium.CustomDataSource('waterLevel');
      let _this = this;
      pointList.forEach(item => {
        let entity = drag.addEntity(item, gloabDataSource);
        _this.poinEntity[item.id] = entity;
      });
      pointList.forEach(item => {
        let temp = this.formatName(item);
        item.names = temp;
        let entitys = drags.addEntity(item, waterLevelSource);
        _this.poinEntitys[item.id] = entitys;
      });
      this.dataSourcesMap['gloabEntry'] = gloabDataSource;
      this.dataSourcesMap['waterLevel'] = waterLevelSource;
      window.viewer.dataSources.add(gloabDataSource);
      window.viewer.dataSources.add(waterLevelSource);
    },
    // 格式化数据
    formatName(point) {
      if (point.type == 'one') {
        return `水位：${point.level || 0} mm\n雨量：${point.level || 0}mm`;
      } else if (point.type == 'two') {
        return `站上水位：${point.level || 0} mm\n站下水位： ${point.level || 0}\n流量： ${point.level || 0}`;
      }
    },
    //三点水库弹窗
    bubble(id) {
      if (this.bubbles) {
        this.bubbles.windowClose();
      }
      this.bubbles = new Bubble(
          Object.assign(this.poinEntity[id], {
            viewer: window.viewer
          })
      );
    },
    //关闭所有弹框
    closeAllPopu() {
      let that = this;
      if (that.bubbles) {
        that.bubbles.windowClose();
      }
    },
    // 淹没分析
    floodAnalyse(val) {
      console.log(val, '下游');
      let waterColor = 'rgba(183, 149, 75, 0.31)';
      let data = xzhqLine;
      var initialPosition = new Cesium.Cartesian3(-2398141.724046622, 5014390.8441055445, 3162478.661400723); // 相机的位置
      var orientation = {
        // 视角
        heading: 5.053815841058131,
        pitch: -0.8535321618334057,
        roll: 6.237595522406176
      };
      var homeCameraView = {
        destination: initialPosition, // 相机的位置
        orientation: orientation
      };
      //设置默认角度
      window.viewer.scene.camera.flyTo(homeCameraView);

      let floodA = new FloodAnalysiss(window.viewer, {
        polygon: data.features[0].geometry.coordinates,
        times_height: [val.minIndex, val.maxIndex],
        waterColor: waterColor,
        show: true,
        pageData: val
      });
      window.submergeA = floodA;
    },
    // 开闸
    sluiceGate() {
    },
    //绘制水面波浪效果
    drawWater() {
      // var initialPosition = new Cesium.Cartesian3(
      //     -2334425.966763559,
      //     5030277.568450616,
      //     3141040.4183633085
      // ); // 相机的位置
      // var orientation = {
      //     // 视角
      //     heading: 4.372493644134752,
      //     pitch: -0.3364551975984358,
      //     roll: 7.840315356943961e-7,
      // };
      // var homeCameraView = {
      //     destination: initialPosition, // 相机的位置
      //     orientation: orientation,
      // };
      // //设置默认角度
      // window.viewer.scene.camera.flyTo(homeCameraView);
      // setTimeout(() => {
      //     this.createWaterSystem({ x: 115.33222244478097, y: 29.84743130583497, z: 10 })
      // }, 1000)

      // const primitive = new Cesium.Primitive(geometryInstances: new Cesium.GeometryInstance(
      //     geometry: new Cesium.EllipseGeometry(
      //         center: Cesium.Cartesian3.fromDegrees(-100.0, 20.0),
      //         semiMinorAxis: 500000.0,
      //         semiMajorAxis: 1000000.0,
      //         rotation: Cesium.Math.PI_OVER_FOUR,
      //         vertexFormat: Cesium.VertexFormat.POSITION_AND_ST
      //     ),
      // ),
      //     appearance: new Cesium.EllipsoidSurfaceAppearance(
      //         material: Cesium.Material.fromType('Stripe')
      //     )

      // );
      // viewer.scene.primitives.add(primitive);

      //开水闸放水效果
      // let openWaterZha = new OpenWaterZha()
      // openWaterZha.open({ lng: 115.33222244478097, lat: 29.84743130583497 })
      // window.viewer.waterZha = openWaterZha
      var initialPosition = new Cesium.Cartesian3(-2334425.966763559, 5030277.568450616, 3141040.4183633085); // 相机的位置
      var orientation = {
        // 视角
        heading: 4.372493644134752,
        pitch: -0.3364551975984358,
        roll: 7.840315356943961e-7
      };
      var homeCameraView = {
        destination: initialPosition, // 相机的位置
        orientation: orientation
      };
      //设置默认角度
      window.viewer.scene.camera.flyTo(homeCameraView);
      let startHeight = 20; // 几何体初始高度
      let startWidth = 100; //初始宽度
      const targetHeight = 35; // 几何体最终的高度
      this.waterEntityRiver = window.viewer.entities.add({
        name: 'river',
        polyline: {
          positions: new Cesium.Cartesian3.fromDegreesArray(this.polylineGeoJson),
          // width: 170,
          extrudedHeight: 200,
          width: new Cesium.CallbackProperty(() => {
            return startWidth;
          }, false),
          followSurface: true,
          material: new Cesium.PolylineTrailLinkMaterialProperty(Cesium.Color.STEELBLUE.withAlpha(0.7), imge2, 10000),
          clampToGround: true,
          distanceDisplayCondition: new Cesium.DistanceDisplayCondition(0, 1600)
        }
      });
      //获取地图高度，实时计算线的宽度
      window.viewer.scene.postRender.addEventListener(function () {
        var position = window.viewer.scene.camera._position;
        console.log(window.viewer.scene.camera.pitch);
        var cartographic = Cesium.Cartographic.fromCartesian(position);
        var currtenHeight = cartographic.height;
        if (currtenHeight > 1053) {
          startWidth = 100;
        } else if (currtenHeight < 1052 && currtenHeight >= 847) {
          startWidth = 110;
        } else if (currtenHeight < 847 && currtenHeight >= 730) {
          startWidth = 135;
        } else if (currtenHeight < 730 && currtenHeight >= 630) {
          startWidth = 140;
        } else if (currtenHeight < 630 && currtenHeight >= 543) {
          startWidth = 160;
        } else if (currtenHeight < 543 && currtenHeight >= 458) {
          startWidth = 190;
        } else if (currtenHeight < 458 && currtenHeight >= 409) {
          startWidth = 220;
        } else if (currtenHeight < 409 && currtenHeight >= 346) {
          startWidth = 240;
        } else if (currtenHeight < 346 && currtenHeight >= 295) {
          startWidth = 290;
        } else if (currtenHeight < 293 && currtenHeight >= 244) {
          startWidth = 350;
        } else if (currtenHeight < 243 && currtenHeight >= 200) {
          startWidth = 380;
        } else if (currtenHeight < 200 && currtenHeight >= 168) {
          startWidth = 420;
        } else if (currtenHeight < 168) {
          startWidth = 560;
        }
      });

      //------------------------------------------面水体流动效果

      this.waterEntity = window.viewer.entities.add({
        name: 'PolylineTrail2',
        polygon: {
          hierarchy: Cesium.Cartesian3.fromDegreesArrayHeights(this.PolygonGeoJson),
          // hierarchy: Cesium.Cartesian3.fromDegreesArrayHeights(new Cesium.CallbackProperty(() => positions, false)),
          perPositionHeight: true,
          clampToGround: true, //贴地
          followSurface: true, //跟随曲面
          material: new Cesium.PolylineTrailLinkMaterialProperty(Cesium.Color.STEELBLUE.withAlpha(0.8), imge2, 20000),
          // material: Cesium.Color.fromBytes(64, 157, 253, 200),
          extrudedHeight: new Cesium.CallbackProperty(() => {
            return startHeight;
          }, false)
        }
      });
      //水面高度实时增加
      this.waterTimer = setInterval(() => {
        if (startHeight < targetHeight) {
          startHeight += 0.7;
          // startWidth += 10;
          if (startHeight >= targetHeight) {
            startHeight = targetHeight;
            // startWidth = targetWidth;
            clearInterval(this.waterTimer);
            // window.viewer.entities.remove(this.waterEntityRiver);
          }
          // 使用该方式会闪烁，改用 Cesium.CallbackProperty 平滑
          // this.waterEntity.polygon.extrudedHeight.setValue(startHeight)
        }
      }, 500);
    },

    // 创建粒子系统
    createWaterSystem(position) {
      // viewer.camera.setView({
      //     destination: Cesium.Cartesian3.fromDegrees(position.x, position.y, position.z),
      //     orientation: {
      //         heading: Cesium.Math.toRadians(0.0),
      //         pitch: Cesium.Math.toRadians(-45),
      //         roll: 0.0
      //     }
      // })
      // console.log(position);
      let gatePosition = Cesium.Cartesian3.fromDegrees(position.x, position.y, position.z);
      let hole = this.viewer.entities.add({position: gatePosition});
      let waterParticleSystem = new Cesium.ParticleSystem({
        image: smoke,
        startColor: Cesium.Color.WHITE.withAlpha(0.0),
        endColor: Cesium.Color.WHITE.withAlpha(0.65),
        startScale: 10,
        endScale: 10,
        minimumParticleLife: 1.5,
        maximumParticleLife: 1.7,
        minimumSpeed: 1.5,
        maximumSpeed: 2.5,
        imageSize: new Cesium.Cartesian2(10, 10),
        emissionRate: 20,
        emitter: new Cesium.CircleEmitter(20.0),
        // emitter: new Cesium.BoxEmitter(new Cesium.Cartesian3(20.0, 5.0, 5.0)),
        modelMatrix: this.computeModelMatrix(hole),
        emitterModelMatrix: this.computeEmitterModelMatrix(...[65, 0, 0]),
        updateCallback: this.updateCallback
        // sizeInMeters: true,
      });
      // 将粒子系统添加到场景中
      // console.log(waterParticleSystem);

      this.viewer.scene.primitives.add(waterParticleSystem);

      // console.log(window.viewer.scene)
    },
    computeModelMatrix(entity) {
      var position = Cesium.Property.getValueOrUndefined(entity.position, Cesium.JulianDate.now());
      let modelMatrix = Cesium.Transforms.eastNorthUpToFixedFrame(position);
      // console.log(modelMatrix);
      return modelMatrix;
    },
    // 计算粒子发射器的位置姿态
    computeEmitterModelMatrix(heading, pitch, roll) {
      // console.log(heading, pitch, roll);
      let hpr = Cesium.HeadingPitchRoll.fromDegrees(heading, pitch, roll);
      let trs = new Cesium.TranslationRotationScale();
      trs.translation = Cesium.Cartesian3.fromElements(0, 0, 0);
      trs.rotation = Cesium.Quaternion.fromHeadingPitchRoll(hpr);
      let Matrix4 = Cesium.Matrix4.fromTranslationRotationScale(trs);
      return Matrix4;
    },
    // 更新粒子运动状态
    updateCallback(p, dt) {
      console.log(p, dt);
      var gravityScratch = new Cesium.Cartesian3();
      var position = p.position;
      Cesium.Cartesian3.normalize(position, gravityScratch);
      Cesium.Cartesian3.fromElements(20 * dt, gravityScratch.y * dt, -30 * dt, gravityScratch);
      p.velocity = Cesium.Cartesian3.add(p.velocity, gravityScratch, p.velocity);
    },
    // getPolygon() {
    //     let geoJson = [
    //         114.88565560050606,
    //         29.688334699279462, 50, 114.88589628714408, 29.688432405756476, 50, 114.88636380922947, 29.688568903184482, 20, 114.88700811190597, 29.688787434689836, 20, 114.88794458880926, 29.689125623307827, 20, 114.8886340711291, 29.68945470167542, 20,
    //         114.88961583098803, 29.689925998071292, 20, 114.88874974584745, 29.691038326012478, 20, 114.88804749391635, 29.690720924623914, 20, 114.88751870623274, 29.6904368372213, 20,
    //         114.88679494595246,
    //         29.690083210599436, 20, 114.88622856074493, 29.68986408148784, 20, 114.8857064899359,
    //         29.68966490265827, 20, 114.88538549582168, 29.68955225587729, 50, 114.88519523518012, 29.689506416601567, 50
    //     ]
    //     return Cesium.Cartesian3.fromDegreesArrayHeights(geoJson)
    // }

    polylineGlow() {
      //加载电子围栏墙数据
      this.ett = window.viewer.entities.add({
        name: '动态立体墙',
        wall: {
          positions: Cesium.Cartesian3.fromDegreesArray(this.WallLineJson),
          // positions: Cesium.Cartesian3.fromDegreesArray([117.154815, 31.853495, 117.181255, 31.854257, 117.182284, 31.848255, 117.184748, 31.840141, 117.180557, 31.835556, 117.180023, 31.833741, 117.166846, 31.833737, 117.155531, 31.833151, 117.154787, 31.835978, 117.151994, 31.839036, 117.150691, 31.8416, 117.151215, 31.844734, 117.154457, 31.848152, 117.154815, 31.853495]),
          maximumHeights: [600, 600, 600, 600, 600, 600, 600, 600, 600, 600, 600, 600, 600, 600, 600, 600, 600, 600],
          minimumHeights: [43.9, 49.4, 38.7, 40, 54, 51, 66.7, 44.6, 41.2, 31.2, 50.1, 53.8, 46.9, 43.9, 40, 40, 40, 40],
          material: new DynamicWallMaterialProperty(weilan, Cesium.Color.ORANGE, 5000)
        }
      });
      window.viewer.flyTo(this.ett);
      // this.lightingShadowInit(window.viewer, 1600)
      // return;
      // window.viewer.entities.add({
      //     polyline: {
      //         positions: Cesium.Cartesian3.fromDegreesArray([
      // 114.8322983314873, 29.671710245649184,
      // 114.83672677142746, 29.668446883870917,
      // 114.84362349107404, 29.668553627655974,
      // 114.85047815664556, 29.66921164004471,
      // 114.86084088388205, 29.670854406897703,
      // 114.86677665540684, 29.6718167707358,
      // 114.88120682899755, 29.67643031303753,
      // 114.89610990629554, 29.687652704096667,
      // 114.8997824355428, 29.69389329993171,
      // 114.90048382255345, 29.69944154402559,
      // 114.8945115709124, 29.70734365551872,
      // 114.86859277070617, 29.70500276813967,
      // 114.84374780802797, 29.694929589552828,
      // 114.8348141543196, 29.691152543341044,
      // 114.82442203269993, 29.691331751762693,
      // 114.82154114077083, 29.673757967753183,
      // 114.82160702562987, 29.668731810522214,
      // 114.8322983314873, 29.671710245649184
      //         ]),
      //         width: 8,
      //         followSurface: true,//跟随曲面
      //         material: new Cesium.PolylineTrailLinkMaterialProperty(Cesium.Color.STEELBLUE, liudong, 5000),
      //         clampToGround: true,//贴地
      //         // material: new Cesium.PolylineGlowMaterialProperty({
      //         //     color: Cesium.Color.DEEPSKYBLUE,
      //         //     glowPower: 0.2
      //         // })
      //     }
      // })
    },
    lightingShadowInit(_viewer, _speed) {
      //日照阴影
      _viewer.scene.globe.enableLighting = true;
      _viewer.shadows = true;
      _viewer.clock.multiplier = _speed;
      //----------------------------------------------------
      // _viewer.scene.globe.enableLighting = true
      // _viewer.shadows = true
      // _viewer.terrainShadows = Cesium.ShadowMode.RECEIVE_ONLY;
      // _viewer.shadowMap.darkness = 0.3 //阴影透明度--越大越透明
      // let time = 0
      // this.inter = setInterval(() => {
      //     // 改变时间设置光照效果
      //     let date = new Date().getTime() + time
      //     let utc = Cesium.JulianDate.fromDate(new Date(date))
      //     //北京时间
      //     _viewer.clockViewModel.currentTime = Cesium.JulianDate.addHours(utc, 0, new Cesium.JulianDate())
      //     time = time + 1000 * 60
      // }, 100)
    },
    PointLight() {
      console.log('光源');
      let scene = window.viewer.scene;
      scene.lightSource.ambientLightColor = new Cesium.Color(0.65, 0.65, 0.65, 1);
      scene.sun.show = false;
      scene.globe.enableLighting = false;
      let position = new Cesium.Cartesian3(-2333612.2271560417, 5030736.924213636, 3140688.427676178);
      let posDeg = Cesium.Cartographic.fromCartesian(position);
      let pointPosition = Cesium.Cartesian3.fromRadians(posDeg.longitude, posDeg.latitude, posDeg.height);
      this.pointEntity = window.viewer.entities.add(
          new Cesium.Entity({
            point: new Cesium.PointGraphics({
              color: new Cesium.Color(1, 1, 1),
              pixelSize: 10,
              outlineColor: new Cesium.Color(1, 1, 1)
            }),
            position: pointPosition
          })
      );
      let options = {
        color: new Cesium.Color(1, 1, 1, 1),
        cutoffDistance: 1000,
        decay: 1,
        intensity: 5
      };
      this.pointLightTest = new Cesium.PointLight(position, options);
      scene.addLightSource(this.pointLightTest);
    },
    handleBeforeUnload(e) {
      e = e || window.event;
      if (e) {
        e.returnValue = '关闭提示';
      }
      // Chrome, Safari, Firefox 4+, Opera 12+ , IE 9+
      return '关闭提示';
    },
    handleUnload() {
      ws_api.disconnectArxServer();
      console.log('刷新');
    },
    listenersArxHandle() {
      if (ws_api) {
        console.log('ws_api=====', ws_api);
        ws_api.subscribeArxInteraction('OnClick_YBSS_Room', msg => {
          //根据指令需求进行处理
          console.log('来自于底板消息==============', msg);
        });
      }
    },
    // UI交互向底板发送消息（如切换相机视角等）
    sendMsg() {
      let command = `VedioParam|300000000|30$`; //来自底板开发人员定义命令参数用该触发底板交互动作
      ws_api.sendArxMessage(command);
    }
  },
  beforeDestroy() {
    window.removeEventListener('beforeunload', this.handleBeforeUnload);
    window.removeEventListener('unload', this.handleUnload);
  },
};
</script>
<style scoped lang="less">
#cesiumContainer {
  width: 100%;
  height: 100%;
}

.cesium-viewer-bottom {
  display: none !important;
}

.cesium-viewer-navigationContainer {
  display: none !important;
}

.config {
  position: absolute;
  top: 10%;
  left: 22%;
  background-color: #fff;
  width: 155px;
  border-radius: 10px;
}

.sm-div-graphic {
  position: absolute;
  color: #fff;
  font-size: 14px;
}

#test .divpoint {
  background: url(../assets/qipao1.png) no-repeat;
  background-size: cover;
  width: 128px;
  height: 216px;
}

.infoWindow {
  height: 80vh;
  width: 70vw;
  position: absolute;
  top: 120px;
  z-index: 999;
  left: 20%;

  iframe {
    width: 100%;
    height: 100%;
  }
}
</style>
