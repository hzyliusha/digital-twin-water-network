<template>
    <div></div>
</template>
<script>
import { Vector as VectorSource } from "ol/source";
import { Vector as VectorLayer } from "ol/layer";
import { Fill, Stroke, Style, Text, Icon } from 'ol/style';
import { GeoJSON } from 'ol/format'
import { Feature, Overlay } from 'ol';
import { Point, Circle, LineString } from 'ol/geom';
import CircleStyle from 'ol/style/Circle';
import { getVectorContext } from "ol/render";
export default {
    data() {
        return {
            route: null,
            geometryMove: '',
            featureMove: {},
            vectorLayer: null,
            distance: 0,
            lastTime: 0,
            speed: 0.1,
            styles: {
                route: new Style({
                    stroke: new Stroke({
                        width: 8,
                        color: "green",
                    }),
                }),
                iconStart: new Style({
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
                    // image: new Icon({
                    //     anchor: [0.5, 1],
                    //     src: require('@/assets/marker-area.png'),
                    //     scale: 0.51, //设置大小
                    // }),
                }),
                iconEnd: new Style({
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
                    // image: new Icon({
                    //     anchor: [0.5, 1],
                    //     src: require('@/assets/marker-area.png'),
                    //     scale: 0.51, //设置大小
                    // }),
                }),
                featureMove: new Style({
                    image: new Icon({
                        anchor: [0.5, 1],
                        src: require('@/assets/close.png'),
                        scale: 0.51, //设置大小
                    }),
                }),
            },
            map: window.map,
        }
    },
    methods: {
        // 画线
        drawHandle(map, coordinateArr) {
            this.map = map;
            this.clearDrawHandle()
            // this.map.getView().setCenter(coordinateArr[0])
            this.route = new LineString(coordinateArr);
            this.geometryMove = new Point(this.route.getFirstCoordinate())
            this.featureMove = new Feature({
                type: "featureMove",
                geometry: this.geometryMove,
            })
            this.vectorLayer = new VectorLayer({
                properties: { name: `routeLine`, id: 'routeLine' },
                zIndex: 28,
                visible: true,
                source: new VectorSource({
                    features: [
                        new Feature({
                            type: "route",
                            geometry: this.route,
                        }),
                        this.featureMove,
                        new Feature({
                            type: "iconStart",
                            geometry: new Point(this.route.getFirstCoordinate()),
                        }),
                        new Feature({
                            type: "iconEnd",
                            geometry: new Point(this.route.getLastCoordinate()),
                        }),
                    ],
                }),
                style: (feature) => {
                    if (feature.get("type") == 'route') {
                        feature.setStyle(this.arrowLineStyles)
                        return
                    }
                    return this.styles[feature.get("type")];
                },
            })
            this.map.addLayer(this.vectorLayer)
            this.startAnimation()
        },
        // 清除绘制
        clearDrawHandle() {
            if (this.vectorLayer) {
                // vectorLayer.value.getSource().clear()
                this.map.removeLayer(this.vectorLayer)
                this.vectorLayer = null
            }
        },

        // 移动 
        moveFeature(e) {
            let time = e.frameState.time;
            this.distance =
                (this.distance + (this.speed * (time - this.lastTime)) / 1000) % 1; //%2表示：起止止起；%1表示：起止起止
            this.lastTime = time;

            const currentCoordinate = this.route.getCoordinateAt(
                this.distance > 1 ? 2 - this.distance : this.distance
            );
            this.geometryMove.setCoordinates(currentCoordinate);
            const vectorContext = getVectorContext(e);
            vectorContext.setStyle(this.styles.featureMove);
            vectorContext.drawGeometry(this.geometryMove);
            this.map.render();
        },

        // 动画开始
        startAnimation() {
            if (this.vectorLayer) {
                this.lastTime = Date.now();
                this.vectorLayer.on("postrender", this.moveFeature);
                this.featureMove.setGeometry(null); //必须用null，不能用{}
            } else {
                // ElMessage.warning('请先绘制路线！')
                this.$message.warning('请先绘制路线！')
            }
        },

        // 动画结束
        stopAnimation() {
            this.featureMove.setGeometry(this.geometryMove);
            this.vectorLayer.un("postrender", this.moveFeature);
        },

        // 箭头样式 当前图层和 放大数
        arrowLineStyles(feature, resolution) {
            let styles = [];
            // 线条样式
            let backgroundLineStyle = new Style({
                stroke: new Stroke({
                    width: 8,
                    color: "green",
                    // lineDash: [10, 25],
                    zIndex: 12
                }),
            });
            styles.push(backgroundLineStyle);
            let geometry = feature.getGeometry();
            // 获取线段长度
            const length = geometry.getLength();
            // 箭头间隔距离（像素）
            const step = 50;
            // 将间隔像素距离转换成地图的真实距离
            const StepLength = step * resolution;
            // 得到一共需要绘制多少个 箭头
            const arrowNum = Math.floor(length / StepLength);
            const rotations = [];
            const distances = [0];
            geometry.forEachSegment(function (start, end) {
                var arrowLonLat = [(end[0] + start[0]) / 2, (end[1] + start[1]) / 2];
                let dx = end[0] - start[0];
                let dy = end[1] - start[1];
                let rotation = Math.atan2(dy, dx);
                distances.unshift(Math.sqrt(dx ** 2 + dy ** 2) + distances[0]);
                rotations.push(rotation);
            });
            // 利用之前计算得到的线段矢量信息，生成对应的点样式塞入默认样式中
            // 从而绘制内部箭头
            for (let i = 1; i < arrowNum; ++i) {
                const arrowCoord = geometry.getCoordinateAt(i / arrowNum);
                const d = i * StepLength;
                const grid = distances.findIndex((x) => x <= d);
                styles.push(
                    new Style({
                        geometry: new Point(arrowCoord),
                        image: new Icon({
                            // src: require('@/assets/close.png'),
                            src: require('@/assets/close.png'),
                            opacity: 1,
                            anchor: [0.5, 0.5],
                            rotateWithView: true,
                            // 读取 rotations 中计算存放的方向信息
                            rotation: -rotations[distances.length - grid - 1],
                            scale: 0.5,
                        }),
                    })
                );
            }
            return styles;
        }
    }
}
</script>
