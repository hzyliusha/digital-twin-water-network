<template>
  <div class="divlabel-container">
    <div class="chart" :id="id"></div>
  </div>
</template>

<script>
// import * as echarts from "echarts"
// eslint-disable-line no-unused-vars
import echarts from 'echarts' // eslint-disable-line no-unused-vars
import 'echarts-liquidfill'
export default {
  name: 'CameraDiv',
  data() {
    return {
      show: true,
      titlex: null
    }
  },
  props: {
    title: {
      type: String,
      default: '标题'
    },
    value: {
      type: Number,
      default: 0.1
    },
    id: {
      type: String,
      default: '001'
    }
  },
  mounted() {
    const options = {
      backgroundColor: '', // 背景色
      title: {
        text: '{a|' + this.title + '}', // 关键代码-传递数值
        subtext: '{b|' + this.value + 'm}', // 关键代码-传递数值
        left: 'center', // 主副标题的水平位置
        top: 10, // 主副标题的垂直位置
        // x: 'center',
        // y: '50%',
        textStyle: {
          rich: {
            a: { // 设置主标题text的样式
              fontSize: '10',
              fontWeight: '400',
              fontFamily: 'Source Han Sans CN',
              color: '#fff'
            }
          }
        },
        subtextStyle: {
          rich: { // 设置副标题subtext的样式
            b: {
              fontSize: '13',
              fontWeight: '400',
              fontFamily: 'Source Han Sans CN',
              color: '#63FAFA'
            }
          }
        }
      },
      series: [{
        type: 'liquidFill', // 配置echarts图类型
        radius: '100%',
        center: ['50%', '50%'],
        //  shape: 'roundRect', // 设置水球图类型（矩形[rect]，菱形[diamond]，三角形[triangle]，水滴状[pin],箭头[arrow]...） 默认为圆形
        data: [0.5, 0.5], // 设置波浪的值
        // waveAnimation:false, // 静止的波浪
        backgroundStyle: {
          color: '#dceff7', // 水球未到的背景颜色
          opacity: 0.7, // 波浪的透明度
          borderWidth: 0,
          borderColor: 'rgba(26,108,177,0.1)'
        },
        outline: {
          show: true,
          borderDistance: 0, // 边框线与图表的距离 数字
          itemStyle: {
            opacity: 0.2, // 边框的透明度   默认为 1
            borderWidth: 2, // 边框的宽度
            shadowBlur: 1, // 边框的阴影范围 一旦设置了内外都有阴影
            shadowColor: '#fff', // 边框的阴影颜色,
            borderColor: '#1e5a7e' // 边框颜色
          }
        },
        color: [ // 波浪颜色
          {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              {
                offset: 1,
                color: 'rgba(6, 187, 112, 0.3)' // 下
              },
              {
                offset: 0,
                color: 'rgba(11, 201, 199, 0.3)'
              }
            ],
            globalCoord: false
          },
          {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              {
                offset: 1,
                color: 'rgba(6, 187, 112, 1)' // 下
              },
              {
                offset: 0,
                color: 'rgba(11, 201, 199, 1)'
              }
            ],
            globalCoord: false
          }
        ],
        // 图形样式
        itemStyle: {
          color: '#3EABFF', // 水球显示的背景颜色
          opacity: 1.0, // 波浪的透明度
          cursor: 'default',
          shadowBlur: 10 // 波浪的阴影范围
        },
        label: {
          normal: {
            formatter: ''
          }
        }
      }
      ]
    }
    this.$nextTick(() => {
      // this.chart = this.$echarts.init(document.getElementById('chart'))
      this.chart = this.$echarts.init(document.getElementById(this.id))
      // var chart = echarts.init(document.getElementById('chart'));
      this.chart.setOption(options)
      window.onresize = function() {
        this.chart.resize()
      }
    })
  },
  methods: {}
}
</script>

<style lang="scss" scoped>
.divlabel-container,
.divlabel-container::before,
.divlabel-container::after {
  z-index: 99;
  position: absolute;
  left: 0;
  bottom: 0;
  cursor: pointer; //手势
}
.chart {
  width: 60px;
  // margin: 20px auto;
  height: 60px;
  // border: 1px solid #D94854;
  animation: cameraMove 1s linear infinite alternate;
  -webkit-animation: cameraMove 1s linear infinite alternate;
}

@keyframes cameraMove {
  from {
    margin-top: 50px;
  }
  to {
    margin-top: 0px;
  }
}
@-webkit-keyframes cameraMove {
  from {
    margin-top: 50px;
  }
  to {
    margin-top: 0px;
  }
}
</style>
