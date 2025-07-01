/*
 * @viewer: 传入地图 例如：viewer.scene
 * @name: 需要查的图层名称 string 例如："fushuishuiku_adjust@DataSourceNew"
 * @LayerIds: 需要隐藏或者显示的图层id [] string  例如:["79", "73", "80", "77", "78", "74"]
 * @visible: 显示和隐藏的bool值   ture| false
 * 
 */
export function MapOnlyObjVisible(viewer, name, LayerIds, visible) {
    let Findlayer = viewer.layers.find(name);
    Findlayer.setOnlyObjsVisible(LayerIds, visible)
}