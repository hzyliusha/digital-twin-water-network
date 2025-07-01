import { defaultValue, Event, createPropertyDescriptor, defined, Property, Color, Cartesian2, Material } from "cesium";

import color1 from '@/assets/image2.png';

export class FlowLineCustomMaterial {
    /**
     * @param options（color 颜色（暂时不叠加），duration 重复时间，trailImage流动图片，repeat 重复次数（Cartesian2） ）
     */
    constructor(options) {
        options = defaultValue(options, defaultValue.EMPTY_OBJECT)

        this._definitionChanged = new Event()
        this._color = undefined
        this._colorSubscription = undefined
        this._time = performance.now()
        this._repeat = undefined;

        this.color = options.color
        this.duration = options.duration
        this.trailImage = options.trailImage
        this.repeat = options.repeat
    }
}

Object.defineProperties(FlowLineCustomMaterial.prototype, {
    isConstant: {
        get: function () {
            return false
        },
    },

    definitionChanged: {
        get: function () {
            return this._definitionChanged
        },
    },

    color: createPropertyDescriptor('color'),
    repeat: createPropertyDescriptor('repeat')
})

FlowLineCustomMaterial.prototype.getType = function () {
    return 'PolylineTrail'
}

FlowLineCustomMaterial.prototype.getValue = function (time, result) {
    if (!defined(result)) {
        result = {}
    }

    result.color = Property.getValueOrClonedDefault(
        this._color,
        time,
        Color.WHITE,
        result.color
    )
    result.image = this.trailImage
    result.time =
        ((performance.now() - this._time) % this.duration) / this.duration
    result.repeat = Property.getValueOrClonedDefault(this._repeat, time, new Cartesian2(1.0, 1.0), result.repeat);

    return result
}

FlowLineCustomMaterial.prototype.equals = function (other) {
    return (
        this === other ||
        (other instanceof FlowLineCustomMaterial &&
            Property.equals(this._color, other._color))
    )
}

Material.PolylineTrailType = 'PolylineTrail'
Material.PolylineTrailImage = color1
Material.PolylineTrailSource =
    'czm_material czm_getMaterial(czm_materialInput materialInput)\n\
                             {\n\
                               czm_material material = czm_getDefaultMaterial(materialInput);\n\
                               vec2 st = repeat * materialInput.st;\n\
                               vec4 colorImage = texture(image, vec2(fract(st.s - time), st.t));\n\
                               material.alpha = 0.8;\n\
                               material.diffuse = colorImage.rgb;\n\
                               return material;\n\
                             }'
// material.alpha = colorImage.a * color.a;?
// vec2 st = materialInput.st;//不设置重复
// material.diffuse = (colorImage.rgb+color.rgb)/2.0;//推按叠加color颜色


Material._materialCache.addMaterial(Material.PolylineTrailType, {
    fabric: {
        type: Material.PolylineTrailType,
        uniforms: {
            color: new Color(1.0, 0.0, 0.0, 0.5),
            image: Material.PolylineTrailImage,
            time: 0,
            repeat: new Cartesian2(1.0, 1.0)
        },
        source: Material.PolylineTrailSource,
    },
    translucent: function () {
        return true
    },
})
