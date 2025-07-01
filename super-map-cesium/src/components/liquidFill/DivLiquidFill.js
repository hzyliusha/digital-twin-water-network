/**
 * @descripion:
 * @param {Viewer} viewer
 * @param {Cartesian2} position
 * @param {String} title
 * @param {String} id
 * @return {*}
 */

import Vue from "vue";
import LiquidFillDiv from "./LiquidFillDiv.vue";
let WindowVm = Vue.extend(LiquidFillDiv);

export default class DivLiquidFill {
    constructor(val) {
        this.viewer = val.viewer;
        this.height = val.height;
        this.position = Cesium.Cartesian3.fromDegrees(
            val.position[0],
            val.position[1],
            val.position[2]
        );
        // console.log("this.viewer", this.viewer)
        // console.log("this.height", this.height)
        // console.log("this.position", this.position)

        let title = val.title;
        let value = val.value ;
        let id = val.id ;
        // console.log("title", title)
        // console.log("id", id)
        this.vmInstance = new WindowVm({
            propsData: {
                title,
                value,
                id
            }
        }).$mount(); //根据模板创建一个面板   定义一个id为的div，这个div就是一个容器，将来vue实例对象中的内容会被挂载到这个容器上  el: '#app',则不用 $mount方法来挂载

        val.viewer.cesiumWidget.container.appendChild(this.vmInstance.$el); //将字符串模板生成的内容添加到DOM上
        // this.viewer.scene.globe.depthTestAgainstTerrain = true
        // val.viewer.container.appendChild(this.vmInstance.$el); //将字符串模板生成的内容添加到DOM上
        this.addPostRender();
    }
    //添加场景事件
    addPostRender() {
        this.viewer.scene.postRender.addEventListener(this.postRender, this);
        // this.viewer.camera.moveEnd.addEventListener(this.onMoveendMap);
    }

    //场景渲染事件 实时更新窗口的位置 使其与笛卡尔坐标一致
    postRender() {
        if (!this.vmInstance.$el || !this.vmInstance.$el.style) return;
        const canvasHeight = this.viewer.scene.canvas.height;
        const canvasWidth = this.viewer.scene.canvas.width;
        const windowPosition = new Cesium.Cartesian2();
        Cesium.SceneTransforms.wgs84ToWindowCoordinates(
            this.viewer.scene,
            this.position,
            windowPosition
        );
        // this.vmInstance.$el.style.bottom =
        //     canvasHeight - windowPosition.y + this.height + "px";
        // const elWidth = this.vmInstance.$el.offsetWidth;
        // this.vmInstance.$el.style.left = windowPosition.x - elWidth / 2 + "px";
        //  this.vmInstance.$el.style.bottom =
        //     canvasHeight - windowPosition.y - this.height + "px";
        let width = document.documentElement.cilentWidth || document.body.clientWidth;

        let clientHeight = document.documentElement.cilentHeight || document.body.clientHeight;

        // this.vmInstance.$el.style.bottom =
        // (canvasHeight - windowPosition.y  - this.height) + "px";
        this.vmInstance.$el.style.bottom =
        (clientHeight - windowPosition.y  - this.height) + "px";
        const elWidth = this.vmInstance.$el.offsetWidth;
        this.vmInstance.$el.style.left = windowPosition.x - elWidth / 2+ "px";
        // console.log("this.vmInstance.$el.style.bottom", this.vmInstance.$el.style.bottom)
        // console.log("this.vmInstance.$el.style.left", this.vmInstance.$el.style.left)
        const camerPosition = this.viewer.camera.position;
        let height = this.viewer.scene.globe.ellipsoid.cartesianToCartographic(camerPosition).height;
        height += this.viewer.scene.globe.ellipsoid.maximumRadius;
        if ((!(Cesium.Cartesian3.distance(camerPosition, this.position) > height)) && this.viewer.camera.positionCartographic.height < 100000) {
            this.vmInstance.$el.style.display = "block";
        } else {
            this.vmInstance.$el.style.display = "none";
        }
        this.onMoveendMap();
        // this.viewer.scene.globe.depthTestAgainstTerrain = true
        // console.log("this.viewer完成", this.viewer)
    }

    heightToZoom(height) {
        var A = 40487.57;
        var B = 0.00007096758;
        var C = 91610.74;
        var D = -40467.74;
        return Math.round(D + (A - D) / (1 + Math.pow(height / C, B)));
    }

    onMoveendMap() {
        //获取当前相机高度
        // let height = Math.ceil(this.viewer.camera.positionCartographic.height);
        let height = Math.ceil(this.viewer.camera.positionCartographic.height);
        let zoom = this.heightToZoom(height);
        if (zoom <= 7) {
            this.vmInstance.$el.style.display = "none"
        }
        else {
            this.vmInstance.$el.style.display = "block"
        }
    }

    //关闭
    windowClose() {
      console.log("哎哎哎哎哎")
        if (this.vmInstance) {
            this.vmInstance.$el.remove();
            this.vmInstance.$destroy();
        }
        //this.vmInstance.$el.style.display = "none"; //删除dom
        this.viewer.scene.postRender.removeEventListener(this.postRender, this); //移除事件监听
    }
}
