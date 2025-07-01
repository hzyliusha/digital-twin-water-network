

const state = {
    geogRegion: [],
    points: [],
    routeLine: [],
    preview: [],
}

const mutations = {
    SET_GEOGREGION: (state, status) => {
        state.geogRegion = status
    },
    SET_POINTS: (state, status) => {
        state.points = status
    },
    SET_ISSHOWLINE: (state, status) => {
        state.routeLine = status
    },
    SET_PREVIEW: (state, status) => {
        state.preview = status
    }
}
const actions = {
    getPoints({ commit }, pointArr) {
        commit('SET_POINTS', pointArr)
    },
    setRegion({ commit }, regionArr) {
        commit('SET_GEOGREGION', regionArr)
    },
}

export default {
    namespaced: true,
    state,
    mutations,
    actions
}
