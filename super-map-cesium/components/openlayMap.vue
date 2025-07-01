<template>
    <div>
        <div class="openlayMap" id="openlayMap"></div>
        <div class="ol-popup" ref="popupTime" id="overLayDom" v-show="showPop">
            <el-row>
                <el-col :span="18">设备描述：</el-col>
                <el-col :span="6">
                    <a href="#" id="popup-close" class="ol-popup-closer" @click="closePop"></a>
                </el-col>
            </el-row>
        </div>
        <RouteLines ref="routeLine" />
        <WaterFlow ref="waterFlow" />
    </div>
</template>

<script>
import { Tile as TileLayer, Vector as VectorLayer, Image as ImageLayer } from 'ol/layer';
// import { TileSuperMapRest, GetFeaturesByGeometryParameters, FeatureService, GetFeaturesBySQLParameters, GetFeaturesByIDsParameters, EditFeaturesParameters } from '@supermap/iclient-ol';
import {TileSuperMapRest} from '@supermap/iclient-ol'
import { Vector as VectorSource } from 'ol/source';
import 'ol/ol.css';
import { Fill, Stroke, Style, Text, Icon } from 'ol/style';
import { Point, Circle, LineString } from 'ol/geom';
import Map from 'ol/Map';
import View from 'ol/View';
import XYZ from 'ol/source/XYZ';
import { defaults as defaultControls, ScaleLine } from 'ol/control';
import CircleStyle from 'ol/style/Circle';
import Feature from 'ol/Feature';
import OSM from 'ol/source/OSM';
import { GeoJSON } from 'ol/format';
import * as turf from '@turf/turf';
import RainFall from '../components/openlayerCom/rainfall';
import RouteLines from '../components/openlayerCom/routeLines';
import WaterFlow from '../components/openlayerCom/waterFlow';
import Overlay from 'ol/Overlay';
import { getVectorContext } from 'ol/render';
import { mapActions, mapGetters, mapMutations, mapState } from 'vuex';
let that = this;
export default {
    name: 'map2D',
    components: {
        RouteLines,
        WaterFlow
    },
    data() {
        return {
            map: null,
            vectors: null,
            layers: null,
            // geogRegion: [],
            rainFall: [],
            showPop: false,
            popupLayer: null,
            featuresArr: []
        };
    },
    created() {},
    computed: {
        ...mapState('olMap', ['geogRegion']),
        ...mapGetters(['points', 'preview']),
        ...mapGetters(['routeLine'])
    },
    mounted() {
        this.init();
        // this.$bus.on('geogRegionChange', val => {
        //     this.geogRegion = val ? val : [];
        // })
        this.$bus.on('rainFallChange', val => {
            this.rainFall = val ? val : [];
        });
    },
    methods: {
        init() {
            // console.log(process.env.VUE_APP_MAP_URL, process.env.VUE_APP_ENV)
            let MAP_TOKEN = 'fb5cce5a710104e6dc922d648ba26699';
            // 天地图影像
            // const mlayer = new TileLayer({
            //     name: "影像(一张图)",
            //     source: new TileSuperMapRest({
            //         url: `http://10.42.6.90:8090/iserver/services/map-YXFW/rest/maps/YXDOM?prjCoordSys=%7B%22epsgCode%22:4326%7D`,
            //         wrapX: true
            //     }),
            //     properties: { name: "影像(一张图)", id: 'v01', type: 'vector' },
            //     visible: true
            // });
            const TiandiMap_vec = new TileLayer({
                name: '天地图矢量图层',
                source: new TileSuperMapRest({
                    url: `http://36.135.21.38:10151/iserver/services/map-china400/rest/maps/China_4326`,
                    wrapX: true
                }),
                properties: { name: '天地图矢量图层', id: 'v01', type: 'vector' },
                visible: false
            });
            const TiandiMap_img = new TileLayer({
                name: '天地图影像图层',
                source: new XYZ({
                    url: `http://t{0-7}.tianditu.com/DataServer?T=img_w&x={x}&y={y}&l={z}&tk=${MAP_TOKEN}`,
                    wrapX: true
                }),
                properties: { name: '天地图影像图层', id: 'v01', type: 'img' },
                visible: true
            });

            const TiandiMap_imgLabel = new TileLayer({
                name: '天地图影像注记',
                source: new XYZ({
                    url: `http://t{0-7}.tianditu.com/DataServer?T=cia_w&tk=${MAP_TOKEN}&x={x}&y={y}&l={z}`,
                    wrapX: true
                }),
                properties: { name: '天地图影像注记', id: 'v01', type: 'img' },
                visible: true
            });

            const TiandiMap_ter = new TileLayer({
                name: '天地图地形图层',
                source: new XYZ({
                    url: `http://t{0-7}.tianditu.com/DataServer?T=ter_w&x={x}&y={y}&l={z}&tk=${MAP_TOKEN}`,
                    wrapX: true
                }),
                properties: { name: '天地图地形图层', id: 'v01', type: 'terrain' },
                visible: false
            });

            const TiandiMap_terLabel = new TileLayer({
                name: '天地图地形注记',
                source: new XYZ({
                    url: `http://t{0-7}.tianditu.com/DataServer?T=cta_w&x={x}&y={y}&l={z}&tk=${MAP_TOKEN}`,
                    wrapX: true
                }),
                properties: { name: '天地图地形注记', id: 'v01', type: 'terrain' },
                visible: false
            });
            // 行政区划
            const bj = new TileLayer({
                name: '行政区划',
                source: new TileSuperMapRest({
                    url: 'http://10.42.6.90:8090/iserver/services/map-country-water-supply-2022/rest/maps/country-water-supply-2022?prjCoordSys=%7B%22epsgCode%22:4326%7D',
                    wrapX: true
                }),
                properties: { name: 'country', id: 'v02', type: 'vector' },
                visible: true
            });
            const ly = new TileLayer({
                name: '流域',
                source: new TileSuperMapRest({
                    url: `http://36.135.21.38:10151/iserver/services/map-fushuierwei/rest/maps/fssk_lyfw?prjCoordSys=%7B%22epsgCode%22:4326%7D`,
                    wrapX: true
                }),
                properties: { name: '流域', id: 'v03', type: 'custom' },
                visible: true
            });
            const sk = new TileLayer({
                name: '水库',
                source: new TileSuperMapRest({
                    url: `http://36.135.21.38:10151/iserver/services/map-fushuierwei/rest/maps/fssk_rsrv?prjCoordSys=%7B%22epsgCode%22:4326%7D`,
                    wrapX: true
                }),
                properties: { name: 'rsrv', id: 'v04', type: 'custom' },
                visible: true
            });
            const xzhq = new TileLayer({
                name: '蓄滞洪区',
                source: new TileSuperMapRest({
                    url: `http://36.135.21.38:10151/iserver/services/map-fushuierwei/rest/maps/fssk_xzhq?prjCoordSys=%7B%22epsgCode%22:4326%7D`,
                    wrapX: true
                }),
                properties: { name: '蓄滞洪区', id: 'v05', type: 'custom' },
                visible: true
            });

            const lxfw = new TileLayer({
                name: '流域范围',
                source: new TileSuperMapRest({
                    url: 'http://36.135.21.38:10151/iserver/services/map-fushuierwei/rest/maps/fssk_lyfw?prjCoordSys=%7B%22epsgCode%22:4326%7D',
                    wrapX: true
                }),
                properties: { name: '流域范围', id: 'v06', type: 'custom' },
                visible: true
            });

            const hl1 = new TileLayer({
                name: '河流水系_拆分1',
                source: new TileSuperMapRest({
                    url: 'http://36.135.21.38:10151/iserver/services/map-fushuierwei/rest/maps/fssk_river_1?prjCoordSys=%7B%22epsgCode%22:4326%7D',
                    wrapX: true
                }),
                properties: { name: 'river', id: 'v07', type: 'custom' },
                visible: true
            });

            const hl2 = new TileLayer({
                name: '河流水系_拆分2',
                source: new TileSuperMapRest({
                    url: 'http://36.135.21.38:10151/iserver/services/map-fushuierwei/rest/maps/fssk_river_2?prjCoordSys=%7B%22epsgCode%22:4326%7D',
                    wrapX: true
                }),
                properties: { name: '河流水系_拆分2', id: 'v08', type: 'custom' },
                visible: true
            });

            const dike = new TileLayer({
                name: '提防',
                source: new TileSuperMapRest({
                    url: 'http://36.135.21.38:10151/iserver/services/map-fushuierwei/rest/maps/fssk_dike?prjCoordSys=%7B%22epsgCode%22:4326%7D',
                    wrapX: true
                }),
                properties: { name: '提防', id: 'dike', type: 'custom' },
                visible: true
            });
            const hp = new TileLayer({
                name: '湖泊',
                source: new TileSuperMapRest({
                    url: 'http://36.135.21.38:10151/iserver/services/map-fushuierwei/rest/maps/fssk_lake?prjCoordSys=%7B%22epsgCode%22:4326%7D',
                    wrapX: true
                }),
                properties: { name: 'lake', id: 'v10', type: 'custom' },
                visible: true
            });
            console.log(...this.geogRegion, 'this.geogRegion');
            this.map = new Map({
                // layers: [mlayer, bj, ly, sk, xzhq, lxfw, hl1, hl2, hp, df],
                layers: [TiandiMap_img, TiandiMap_imgLabel],
                target: 'openlayMap', //对应div容器的id
                view: new View({
                    center: [114.913915264092, 29.5459289970998], //地图中心点
                    zoom: 11, //缩放层级
                    // maxZoom: 18,
                    projection: 'EPSG:4326' //坐标系
                }),
                controls: defaultControls({
                    zoom: false
                }).extend([
                    new ScaleLine({
                        units: 'metric'
                    })
                ])
            });

            let that = this;
            let minZoom = 11;
            let maxZoom = 14;

            // 地图点击事件
            that.map.on('click', function (e) {
                console.log(e);
                that.map.forEachFeatureAtPixel(
                    e.pixel,
                    (feature,layer) => {
                        console.log(feature.getGeometry())
                        console.log(feature.getProperties(),layer);
                    },
                    { hitTolerance: 50 }
                );
                // const coordinate = that.map.getCoordinateFromPixel(e.pixel)
                let allLayer = that.map.getLayers().getArray();
                console.log(allLayer, 'allLayer')
                allLayer.forEach(item => {
                    console.log(item.getProperties().id, 'item')
                    let layerId = item.getProperties().id;
                    if (layerId == 'dike') {
                        let x = e.coordinate[0]; //获取点击处的经度
                        let y = e.coordinate[1]; //获取点击处的纬度
                        var point = new Point([x, y]); //构造点几何图形
                        let datasetNames = ['dike:intersect_dike'];
                        // that.getMapData(point, datasetNames)
                    } else if (layerId == 'rainFall') {
                        // 降雨等值面
                        console.log('rainFall');
                    } else if (layerId == 'point') {
                        let getPoint = that.vectors.getFeatures().filter(r => r.getProperties());
                        console.log(getPoint, 'getPoint');
                        // 地图打点数据
                        that.map.forEachFeatureAtPixel(
                            e.pixel,
                            feature => {
                                let getFeature = feature.getProperties();
                                if (getFeature.type == 'points') {
                                    console.log(getFeature, 'features');
                                    if (that.popupLayer) {
                                        const { status } = that.popupLayer.getProperties();
                                        if (getFeature.type == status) {
                                            that.closePop();
                                        }
                                    }
                                    that.showPop = true;
                                    that.createOverlay(getFeature);
                                }
                            },
                            { hitTolerance: 5 }
                        );
                    }
                });
            });

            // 地图滚轮事件
            // that.map.on('moveend', function (e) {
            //     const zoom = that.map.getView().getZoom();
            //     // 调整视图以适应给定的几何体或范围
            //     if (zoom >= minZoom && zoom <= maxZoom) {
            //         // 显示图层
            //         let getLayer = that.map.getLayers().getArray();
            //         let temp = getLayer.find(item => item.getProperties().id == 'v07');
            //         temp.setVisible(true)
            //     } else {
            //         // 隐藏图层
            //         let getLayer = that.map.getLayers().getArray();
            //         let temp = getLayer.find(item => item.getProperties().id == 'v07');
            //         temp.setVisible(false);
            //     }
            // });
            // 监听地图zoom变化
            that.map.getView().on('change:resolution', function (e) {
                var zoom = that.map.getView().getZoom();
                // console.log(zoom, "zoom")
                //整数校验
                if (Math.floor(zoom) === zoom) {
                    if (zoom < 12) {
                        //刷新图层：避免图形（圆）随地图层级缩放
                        setTimeout(function () {
                            // Vector1.getSource().clear();
                            // Vector1.setSource(source1);
                            // Vector1.getSource().changed();
                        }, 100);
                    }
                }
            });

            // let datasetNames = ["dike:intersect_dike"];
            // let dataUrl = 'http://36.135.21.38:10151/iserver/services/data-fushuierwei/rest/data';
            // let idsParam = new GetFeaturesBySQLParameters({
            //     datasetNames: datasetNames, //查询的数据源：数据集（固定，无需修改）
            //     // spatialQueryMode: "WITHIN",//查询条件
            //     // IDs: [200, 199]
            //     queryParameter: {
            //         // attributeFilter: "ID in (420222000175,420222000227)"
            //         attributeFilter: "ID in (420222000175)"
            //     },
            //     maxFeatures: 1000,
            // })
            // var features = new FeatureService(dataUrl).getFeaturesBySQL(idsParam, (serviceResult) => {
            //     let vectorSource = new VectorSource({
            //         features: (new GeoJSON()).readFeatures(serviceResult.result.features),
            //         wrapX: true,
            //     });

            //     let features = vectorSource.getFeatures();
            //     features.map(item=>{
            //         // vectorSource.removeFeature(item);
            //         item.setStyle(new Style({
            //             stroke: new Stroke({
            //                 color: "rgba(255, 255, 255, 1)",
            //                 width: 20
            //             }),
            //             fill: new Fill({ //矢量图层填充颜色，以及透明度
            //                 color: 'rgba(255, 255, 255, 0.1)'
            //             }),
            //         }))
            //     })
            //     console.log(vectorSource,"vectorSource")
            //     that.layers = new VectorLayer({
            //         source: vectorSource,
            //         zIndex: 20,
            //         id: 'areaDatas',
            //         visible: true,
            //     });
            //     that.map.addLayer(that.layers);
            //     // let editFeaturesArr = new EditFeaturesParameters({
            //     //     features: new GeoJSON().readFeatures(serviceResult.result.features),
            //     //     dataSourceName: "dike",
            //     //     dataSetName: "intersect_dike",
            //     //     editType: "delete",
            //     //     isUseBatch: true,
            //     //     returnContent: false,
            //     //     // IDs: [420222000175]
            //     // })
            //     // new FeatureService(dataUrl).editFeatures(editFeaturesArr).then(editService=>{
            //     //     console.log(editService,"editService")
            //     //     if (serviceResult.result.succeed) {
            //     //         this.$message.success('修改成功');
            //     //     }
            //     //     const dike = new TileLayer({
            //     //         name: "提防",
            //     //         source: new TileSuperMapRest({
            //     //             url: 'http://36.135.21.38:10151/iserver/services/map-fushuierwei/rest/maps/fssk_dike?prjCoordSys=%7B%22epsgCode%22:4326%7D',
            //     //             wrapX: true
            //     //         }),
            //     //         properties: { name: "提防", id: 'dike', type: 'custom' },
            //     //         visible: true
            //     //     });
            //     //     that.map.addLayer(dike);
            //     // })
            // })
        },
        polygonStyle(feature) {
            var style = new Style({
                fill: new Fill({
                    //矢量图层填充颜色，以及透明度
                    color: '#000'
                }),
                stroke: new Stroke({
                    //边界样式
                    lineDash: [6], //注意:该属性为虚线效果，在IE10以上版本才有效果
                    color: '#000',
                    width: 2
                })
                // text: new Text({ //文本样式
                //     font: '20px Verdana,sans-serif',
                //     text:feature.id,
                //     fill: new Fill({
                //     color: '#000'
                //     })
                // })
            });
            return style;
        },
        // 点击图层获取数据片段
        getMapData(pointArr, datasetNames) {
            let that = this;
            let getArea = that.map.getLayers().getArray();
            let findData = getArea.find(item => item.getProperties().id == 'areaData');
            // return
            if (!findData) {
                let dataUrl = 'http://36.135.21.38:10151/iserver/services/data-fushuierwei/rest/data';
                var geometryParam = new GetFeaturesByGeometryParameters({
                    datasetNames: datasetNames, //查询的数据源：数据集（固定，无需修改）
                    geometry: pointArr, //查询几何
                    spatialQueryMode: 'WITHIN' //查询条件
                });
                new FeatureService(dataUrl).getFeaturesByGeometry(geometryParam, serviceResult => {
                    console.log(serviceResult, 'serviceResult');
                    if (serviceResult.result.features.features.length) {
                        let vectorSource = new VectorSource({
                            features: new GeoJSON().readFeatures(serviceResult.result.features),
                            wrapX: false
                        });
                        that.layers = new VectorLayer({
                            source: vectorSource,
                            zIndex: 22,
                            id: 'areaData',
                            visible: true
                        });
                        that.map.addLayer(that.layers);
                    }
                });
            } else {
                that.map.removeLayer(findData);
            }
        },
        // 点击点位展示详情弹窗
        createOverlay(getFeature) {
            let that = this;
            let popupDia = document.getElementById('overLayDom');
            that.popupLayer = new Overlay({
                element: popupDia,
                id: 'TimeDialog',
                position: [getFeature.lgtd, getFeature.lttd],
                positioning: 'center-center',
                // offset: [-325, -25],
                offset: [-100, 0]
            });

            that.popupLayer.setProperties({ status: 'points' });
            that.map.addOverlay(that.popupLayer);
            // let popupCloser = document.getElementById('popup-close');
            // // 关闭弹窗
            // popupCloser.addEventListener('click', () => {
            //     that.popupLayer.setPosition(undefined);
            // })
            // getHistoryData(feature.getProperties());
        },
        // 关闭实时检测站弹框
        closePop() {
            let that = this;
            that.popupLayer = null;
            that.map.removeOverlay(that.popupLayer);
            that.showPop = false;
        }
    },

    watch: {
        // 监听图层选中
        geogRegion: {
            immediate: true,
            deep: true,
            handler(newVal, oldVal) {
                let that = this;
                if (that.map) {
                    const allLayer = that.map.getLayers().getArray();
                    if (oldVal.length > newVal.length) {
                        // 取消选中图层时
                        const notLayer = oldVal.filter(r => !newVal.find(c => c === r));
                        notLayer.length &&
                            allLayer.forEach(c => {
                                notLayer.forEach(b => {
                                    if (c.getProperties().id === b) {
                                        that.map.removeLayer(c); // 删除取消选中的图层
                                    }
                                });
                            });
                    } else {
                        // 点击选中图层时
                        const selectLayer = newVal.filter(r => !allLayer.find(c => c.getProperties().id == r));
                        selectLayer.forEach(r => {
                            switch (r) {
                                case 'country': // 行政区划
                                    const bj = new TileLayer({
                                        name: '阳新县行政区划',
                                        source: new TileSuperMapRest({
                                            url: 'http://36.135.21.38:10151/iserver/services/map-fushuierwei/rest/maps/tsyx_xzqh?prjCoordSys=%7B%22epsgCode%22:4326%7D',
                                            wrapX: true
                                        }),
                                        zIndex: 20,
                                        properties: { name: 'country', id: 'country', type: 'vector' },
                                        visible: true
                                    });
                                    that.map.addLayer(bj);
                                    break;
                                case 'river': // 大型水库
                                    const hl = new TileLayer({
                                        name: '河流水系',
                                        source: new TileSuperMapRest({
                                            url: 'http://36.135.21.38:10151/iserver/services/map-fushuierwei/rest/maps/fssk_river?prjCoordSys=%7B%22epsgCode%22:4326%7D',
                                            wrapX: true
                                        }),
                                        zIndex: 20,
                                        properties: { name: 'river', id: 'river', type: 'custom' },
                                        visible: true
                                    });
                                    that.map.addLayer(hl);
                                    break;
                                case 'river1': // 中型水库
                                    const hl1 = new TileLayer({
                                        name: '河流水系_拆分1',
                                        source: new TileSuperMapRest({
                                            url: 'http://36.135.21.38:10151/iserver/services/map-fushuierwei/rest/maps/fssk_river_1?prjCoordSys=%7B%22epsgCode%22:4326%7D',
                                            wrapX: true
                                        }),
                                        zIndex: 20,
                                        properties: { name: 'river1', id: 'river1', type: 'custom' },
                                        visible: true
                                    });
                                    that.map.addLayer(hl1);
                                    break;
                                case 'river2': // 河流
                                    const hl2 = new TileLayer({
                                        name: '河流水系_拆分2',
                                        source: new TileSuperMapRest({
                                            url: 'http://36.135.21.38:10151/iserver/services/map-fushuierwei/rest/maps/fssk_river_2?prjCoordSys=%7B%22epsgCode%22:4326%7D',
                                            wrapX: true
                                        }),
                                        zIndex: 20,
                                        properties: { name: 'river2', id: 'river2', type: 'custom' },
                                        visible: true
                                    });
                                    that.map.addLayer(hl2);
                                    break;
                                case 'river3': // 长江
                                    const cj = new TileLayer({
                                        name: '河流水系_拆分3',
                                        source: new TileSuperMapRest({
                                            url: 'http://36.135.21.38:10151/iserver/services/map-fushuierwei/rest/maps/fssk_river_3?prjCoordSys=%7B%22epsgCode%22:4326%7D',
                                            wrapX: true
                                        }),
                                        zIndex: 20,
                                        properties: { name: 'river3', id: 'river3', type: 'custom' },
                                        visible: true
                                    });
                                    that.map.addLayer(cj);
                                    break;
                                case 'lake': // 湖泊
                                    const hp = new TileLayer({
                                        name: '湖泊',
                                        source: new TileSuperMapRest({
                                            url: 'http://36.135.21.38:10151/iserver/services/map-fushuierwei/rest/maps/fssk_lake?prjCoordSys=%7B%22epsgCode%22:4326%7D',
                                            wrapX: true
                                        }),
                                        zIndex: 20,
                                        properties: { name: 'lake', id: 'lake', type: 'custom' },
                                        visible: true
                                    });
                                    that.map.addLayer(hp);
                                    break;
                                // case 'rsrv': // 水库
                                //     const sk = new TileLayer({
                                //         name: "水库",
                                //         source: new TileSuperMapRest({
                                //             url: `http://36.135.21.38:10151/iserver/services/map-fushuierwei/rest/maps/fssk_rsrv?prjCoordSys=%7B%22epsgCode%22:4326%7D`,
                                //             wrapX: true
                                //         }),
                                //         zIndex: 20,
                                //         properties: { name: "rsrv", id: 'rsrv', type: 'custom' },
                                //         visible: true
                                //     });
                                //     that.map.addLayer(sk);
                                //     break;
                                case 'dike': // 堤防
                                    const df = new TileLayer({
                                        name: '堤防',
                                        source: new TileSuperMapRest({
                                            url: 'http://36.135.21.38:10151/iserver/services/map-fushuierwei/rest/maps/fssk_dike?prjCoordSys=%7B%22epsgCode%22:4326%7D',
                                            wrapX: true
                                        }),
                                        zIndex: 20,
                                        properties: { name: 'dike', id: 'dike', type: 'custom' },
                                        visible: true
                                    });
                                    that.map.addLayer(df);
                                    break;
                                case 'xzhq': // 蓄滞洪区
                                    const xzhq = new TileLayer({
                                        name: '蓄滞洪区',
                                        source: new TileSuperMapRest({
                                            url: 'http://36.135.21.38:10151/iserver/services/map-fushuierwei/rest/maps/fssk_xzhq?prjCoordSys=%7B%22epsgCode%22:4326%7D',
                                            wrapX: true
                                        }),
                                        zIndex: 20,
                                        properties: { name: 'xzhq', id: 'xzhq', type: 'custom' },
                                        visible: true
                                    });
                                    that.map.addLayer(xzhq);
                                    break;
                                case 'lyfw': // 流域范围
                                    const lyfw = new TileLayer({
                                        name: '流域范围',
                                        source: new TileSuperMapRest({
                                            url: `http://36.135.21.38:10151/iserver/services/map-fushuierwei/rest/maps/fssk_lyfw?prjCoordSys=%7B%22epsgCode%22:4326%7D`,
                                            wrapX: true
                                        }),
                                        properties: { name: 'lyfw', id: 'lyfw', type: 'custom' },
                                        visible: true
                                    });
                                    that.map.addLayer(lyfw);
                                    break;
                                case 'lyfwTransparent': // 流域范围透明度
                                    const lyfwT = new TileLayer({
                                        name: '流域范围',
                                        source: new TileSuperMapRest({
                                            url: `http://36.135.21.38:10151/iserver/services/map-fushuierwei/rest/maps/fssk_lyfw_generalization?prjCoordSys=%7B%22epsgCode%22:4326%7D`,
                                            wrapX: true
                                        }),
                                        properties: { name: 'lyfwTransparent', id: 'lyfwTransparent', type: 'custom' },
                                        visible: true
                                    });
                                    that.map.addLayer(lyfwT);
                                    break;
                            }
                        });
                    }
                }
            }
        },
        // 监听是否显示降雨分布图
        rainFall: {
            handler(newVal, oldVal) {
                let that = this;
                if (that.map) {
                    const allLayer = that.map.getLayers().getArray();
                    if (oldVal.length > newVal.length) {
                        // 取消选中图层时
                        const notLayer = oldVal.filter(r => !newVal.find(c => c === r));
                        notLayer.length &&
                            allLayer.forEach(c => {
                                notLayer.forEach(b => {
                                    if (c.getProperties().id === b) {
                                        that.map.removeLayer(c); // 删除取消选中的图层
                                    }
                                });
                            });
                    } else {
                        const selectLayer = newVal.filter(r => !allLayer.find(c => c.getProperties().id == r));
                        if (selectLayer[0] == 'rainFall') {
                            let that = this;
                            let drpJson = require('../static/drp.json');
                            let rainFall = new RainFall(that.map);
                            rainFall.addRainfallMap(drpJson.data);
                        }
                    }
                }
            }
        },
        points: {
            handler(newVal, oldVal) {
                let that = this;
                if (that.map) {
                    const allLayer = that.map.getLayers().getArray();
                    if (oldVal.length > newVal.length) {
                        // 取消选中图层时
                        const notLayer = oldVal.filter(r => !newVal.find(c => c === r));
                        notLayer.length &&
                            allLayer.forEach(c => {
                                notLayer.forEach(b => {
                                    if (c.getProperties().id === b) {
                                        that.map.removeLayer(c); // 删除取消选中的图层
                                    }
                                });
                            });
                    } else {
                        const selectLayer = newVal.filter(r => !allLayer.find(c => c.getProperties().id == r));
                        if (selectLayer[0] == 'point') {
                            let that = this;
                            that.vectors = new VectorSource();
                            const vectorLayer = new VectorLayer({
                                source: this.vectors,
                                properties: { title: `ponitDial`, id: 'point' },
                                style: new Style({
                                    fill: new Fill({
                                        color: 'rgba(249, 231, 159 , 0.2)'
                                    }),
                                    stroke: new Stroke({
                                        color: '#ffcc33',
                                        width: 2
                                    }),
                                    image: new CircleStyle({
                                        radius: 7,
                                        fill: new Fill({
                                            color: 'rgba(2231, 76, 60 , 0.5)'
                                        }),
                                        stroke: new Stroke({
                                            color: '#ffcc33',
                                            width: 2
                                        })
                                    })
                                }),
                                zIndex: 23,
                                visible: true
                            });
                            that.map.addLayer(vectorLayer);
                            let wsJson = require('../static/ws.json');
                            let rainFall = new RainFall(that.map);
                            rainFall.createPoint(wsJson, that.vectors, 'points');
                        }
                    }
                }
            }
        },
        routeLine: {
            handler(newVal, oldVal) {
                let that = this;
                if (that.map) {
                    const allLayer = that.map.getLayers().getArray();
                    if (oldVal.length > newVal.length) {
                        // 取消选中图层时
                        const notLayer = oldVal.filter(r => !newVal.find(c => c === r));
                        notLayer.length &&
                            allLayer.forEach(c => {
                                notLayer.forEach(b => {
                                    if (c.getProperties().id === b) {
                                        that.map.removeLayer(c); // 删除取消选中的图层
                                    }
                                });
                            });
                    } else {
                        const selectLayer = newVal.filter(r => !allLayer.find(c => c.getProperties().id == r));
                        if (selectLayer[0] == 'routeLine') {
                            let jsonData = [
                                {
                                    drp: 10,
                                    lgtd: 114.25,
                                    lttd: 29.5
                                },
                                {
                                    drp: 20,
                                    lgtd: 114.275,
                                    lttd: 29.475
                                },
                                {
                                    drp: 30,
                                    lgtd: 114.3,
                                    lttd: 29.575
                                },
                                {
                                    drp: 40,
                                    lgtd: 114.325,
                                    lttd: 29.625
                                },
                                {
                                    drp: 50,
                                    lgtd: 114.325,
                                    lttd: 29.6
                                },
                                {
                                    drp: 10,
                                    lgtd: 114.325,
                                    lttd: 29.55
                                },
                                {
                                    drp: 20,
                                    lgtd: 114.325,
                                    lttd: 29.525
                                },
                                {
                                    drp: 30,
                                    lgtd: 114.35,
                                    lttd: 29.675
                                },
                                {
                                    drp: 20,
                                    lgtd: 114.35,
                                    lttd: 29.625
                                },
                                {
                                    drp: 10,
                                    lgtd: 114.35,
                                    lttd: 29.6
                                },
                                {
                                    drp: 20,
                                    lgtd: 114.35,
                                    lttd: 29.575
                                },
                                {
                                    drp: 20,
                                    lgtd: 114.35,
                                    lttd: 29.55
                                },
                                {
                                    drp: 30,
                                    lgtd: 114.35,
                                    lttd: 29.525
                                },
                                {
                                    drp: 20,
                                    lgtd: 114.35,
                                    lttd: 29.5
                                },
                                {
                                    drp: 20,
                                    lgtd: 114.35,
                                    lttd: 29.45
                                },
                                {
                                    drp: 50,
                                    lgtd: 114.35,
                                    lttd: 29.4
                                }
                            ];
                            let lineCoord = jsonData.map(item => {
                                return [item.lgtd, item.lttd];
                            });
                            this.$refs.routeLine.drawHandle(that.map, lineCoord);
                        }
                    }
                }
            }
        },
        preview: {
            handler(newVal, oldVal) {
                let that = this;
                if (that.map) {
                    if (oldVal.length > newVal.length) {
                        // 取消选中图层时
                        this.$refs.waterFlow.rmOverlays();
                    } else {
                        this.$refs.waterFlow.createdMap(that.map);
                    }
                }
            }
        }
    }
};
</script>

<style lang="less">
#openlayMap {
    width: 100vw;
    height: 100vh;
    border: solid 1px #000;
}

.ol-popup {
    position: absolute;
    bottom: 22px;
    min-width: 200px;
    min-height: 100px;
    padding: 0px 15px 15px 15px;
    background: #000;
    border-radius: 8px;

    .ol-popup-closer {
        text-decoration: none;
        position: absolute;
        top: 2px;
        right: 8px;
    }

    .ol-popup-closer:after {
        content: '✖';
    }
}
</style>
