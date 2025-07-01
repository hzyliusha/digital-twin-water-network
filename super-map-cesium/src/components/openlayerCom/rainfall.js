import * as turf from '@turf/turf';
import { Vector as VectorSource } from "ol/source";
import { Vector as VectorLayer } from "ol/layer";
import { Fill, Stroke, Style, Text, Icon } from 'ol/style';
import { GeoJSON } from 'ol/format'
import LYBJjSON from '../../static/lybj.json'
import { Feature, Overlay } from 'ol';
import { Point, Circle } from 'ol/geom';
import CircleStyle from 'ol/style/Circle';
/**
 * 降雨分布图
 */
export default class RainFall {
    constructor(map) {
        this.map = map;
    }
    // 将于分布图
    addRainfallMap(drpJson) {
        //从data中获取有效数据生成geojson格式的对象。这里的data是一个对象的数组，这个对象中包含属性long(即x)，lat(即y)，drop(即差值字段)
        let features = drpJson.map(i => {
            return {
                type: 'Feature',
                properties: {
                    value: i.drp
                },
                geometry: {
                    type: 'Point',
                    coordinates: [i.lgtd, i.lttd]
                },
            }
        });
        let points = turf.featureCollection(features);
        let interpolate_options = {//设置生成网格的参数
            gridType: 'points',//使用的几何数据类型
            property: 'value',//插值使用的字段
            units: 'degrees',//横纵坐标的单位
            weight: 5//插值字段的值的权重
        };
        let grid = turf.interpolate(points, 0.02, interpolate_options);//生成网格，0.01是网格的大小
        grid.features.map((i) => (i.properties.value = i.properties.value.toFixed(2)));
        let isobands_options = {//根据上面的网格值生成等值面的参数
            zProperty: 'value',//同样表示插值的字段名
            breaksProperties: [//设置分段后各个段使用的颜色
                { fill: "rgba(227, 227, 225, 0.6)" },
                { fill: "rgba(198, 198, 225, 0.5)" },
                { fill: "rgba(169, 170, 255, 0.5)" },
                { fill: "rgba(142, 142, 255, 0.5)" },
                { fill: "rgba(113, 113, 255, 0.5)" },
                { fill: "rgba(85, 84, 255, 0.5)" },
                { fill: "rgba(57, 57, 255, 0.5)" },
            ],
            commonProperties: {
                "fill-opacity": .2
            },
            type: 'rainFall',
        };
        let isobandData = turf.isobands(//根据上面的网格生成等值面
            grid,
            [0, 10, 20, 30, 40, 50, 70, 80], //根据上面的插值字段的值来进行分段的依据，即这个中间的每一段就设置为对应上面设置的颜色
            isobands_options
        );

        let intersectionFeatures = [];
        let bjArea = turf.flatten(LYBJjSON);
        isobandData = turf.flatten(isobandData);
        // 遍历裁剪
        isobandData.features.forEach(function (layer1, index) {
            bjArea.features.forEach(function (layer2) {
                var intersection = null;
                try {
                    intersection = turf.intersect(layer1, layer2);
                }
                catch (e) {
                    layer1 = turf.buffer(layer1, 0);
                    intersection = turf.intersect(layer1, layer2);
                }
                if (intersection != null) {
                    intersection.properties = layer1.properties;
                    intersection.id = Math.random() * 100000;
                    intersectionFeatures.push(intersection);
                }
            });
        });
        let intersection = turf.featureCollection(intersectionFeatures);
        let vectorSource = new VectorSource({
            features: new GeoJSON().readFeatures(intersection),
        });
        let vectorLayer = new VectorLayer({
            source: vectorSource,
            properties: { title: `rainFallAll`, id: 'rainFall' },
            zIndex: 21,
            visible: true,
            style: (feature) => {
                return new Style({
                    fill: new Fill({
                        color: feature.values_.fill,
                    }),
                });
            },
        });
        this.map.addLayer(vectorLayer);
    }
    // 创建点位
    createPoint = (peoples, vector, type) => {
        if (peoples.data.length == 0) return
        let pointArr = peoples.data.map((item,index) => {
            const feature = new Feature({
                geometry: new Point([item.lgtd, item.lttd]),
                name: index,
            });
            feature.setStyle(
                new Style({
                    image: new CircleStyle({
                        radius: 7,
                        fill: new Fill({
                            color: 'rgba(2231, 76, 60 , 0.5)',
                        }),
                        stroke: new Stroke({
                            color: '#ffcc33',
                            width: 5,
                        }),
                    }),
                    text: new Text({
                        text: `${index}`,
                        textAlign: "center",
                        textBaseline: "middle",
                        font: "14px font-size",
                        fill: new Fill({
                            color: "#fff",
                        }),
                        backgroundFill: new Fill({
                            color: "#0821c3",
                        }),
                        backgroundStroke: new Stroke({
                            color: "rgba(255,255,255,.5)",
                            lineCap: "round",
                            lineJoin: "round",
                            width: 1,
                        }),
                        padding: [6, 30, 4, 30],
                        offsetY: "-21",
                    }),
                })
            );
            feature.setId(`${index}`);
            feature.setProperties({...item, type: type});
            return feature;
        });
        vector.addFeatures(pointArr);
    }
}