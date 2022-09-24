<template>
  <v-container class="my-6" fluid>
    <v-row justify="center" dense v-if="!this.station">
      <v-col class="text-center text-h4 text-capitalize"
        >Dataset Metadata</v-col
      >
    </v-row>
    <v-row
      class="text-center"
      justify="center"
      align="center"
      v-if="!this.station"
    >
      <v-col cols="5">
        <v-select
          v-model="dataset"
          :items="items"
          item-text="text"
          item-value="value"
          label="Select"
          persistent-hint
          single-line
        ></v-select>
      </v-col>
      <v-col cols="2">
        <v-btn color="primary" @click="getMetadata">See</v-btn>
      </v-col>
    </v-row>
    <v-row v-if="datasetSelected && !this.station">
      <v-col class="text-center" v-if="loading">
        <v-progress-circular
          :size="200"
          class="loader"
          color="primary"
          indeterminate
        >
          Trayendo metadata...
        </v-progress-circular>
      </v-col>
      <v-col v-else>
        <v-treeview
          :items="tree_data"
          item-key="id"
          open-on-click
          color="info"
          dense
        >
          <template v-slot:prepend="{ item, open }">
            <v-icon v-if="!item.end">
              {{ open ? 'mdi-folder-open' : 'mdi-folder' }}
            </v-icon>
            <!-- <v-icon v-else>
              {{ files[item.file] }}
            </v-icon> -->
          </template>
          <template v-slot:append="{ item }">
            Ir
            <v-icon v-if="!item.end" @click="openStation(item)" color="primary">
              mdi-arrow-right-thin-circle-outline
            </v-icon>
          </template>
          <template v-slot:label="{ item }">
            <span v-if="item.end">
              <b>{{ item.key }}</b
              >: {{ item.value }}
            </span>
            <span v-else>{{ item.name }}</span>
          </template>
        </v-treeview>
      </v-col>
    </v-row>
    <v-row class="text-center" v-if="!!this.station">
      <v-col>
        <time-series
          v-bind:dataset="dataset"
          v-bind:station="station"
          v-bind:recomendations="recomendations"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
// @ is an alias to /src

import axios from 'axios'
import TimeSeries from '../components/TimeSeries.vue'

export default {
  name: 'MetaData',
  components: { TimeSeries },
  data: () => ({
    items: [
      { text: 'Madrid', value: 'madrid' },
      { text: 'Arequipa', value: 'aqp' },
      { text: 'India', value: 'india' }
    ],
    datasetSelected: false,
    dataset_metadata: {},
    dataset: '',
    station: null,
    tree_data: [],
    recomendations: {},
    loading: false
  }),
  methods: {
    async openStation(item) {
      console.log('Hola', item)
      await this.getRecomendations(this.dataset, item.name)
      this.station = item.name.toLowerCase()
    },
    async getRecomendations(dataset, station) {
      let { data: recomendations } = await axios.get(
        `http://localhost:8080/recomendation/${dataset}/${this.titleCase(
          station
        )}`
      )
      this.recomendations = recomendations
      console.log('Recomendatios:', recomendations)
    },
    titleCase(str) {
      return str.toLowerCase().replace(/\b(\w)/g, s => s.toUpperCase())
    },
    getMetadata() {
      this.datasetSelected = true
      this.loading = true
      axios
        .get(`http://localhost:8080/meta_data/${this.dataset}`)
        .then(async ({ data }) => {
          this.loading = false
          let tree_data = data.map((station, idx) => {
            console.log('Station: ', station)
            let null_pers = Object.keys(station.null_per)
            null_pers = null_pers.map((key, idx) => {
              return {
                id: idx,
                name: `${key}: ${parseFloat(station.null_per[key]).toFixed(
                  2
                )}%`,
                key: key,
                value: parseFloat(station.null_per[key]).toFixed(2) + '%',
                end: true
              }
            })
            let info = Object.keys(station.info)
            info = info.map((key, idx) => {
              return {
                id: idx,
                name: `${key}: ${station.info[key]}`,
                key: key,
                value: station.info[key],
                end: true
              }
            })

            console.log('Nullpers:', null_pers)
            return {
              id: idx,
              name: station.station_name,
              children: [
                {
                  id: 1,
                  name: `Info:`,
                  children: info
                },
                {
                  id: 2,
                  name: `Features:`,
                  children: station.features.map((feat, idx) => {
                    return { id: idx, name: feat }
                  })
                },
                {
                  id: 3,
                  name: 'Null Rate',
                  children: null_pers
                }
              ]
            }
          })
          console.log(tree_data)

          let feats = data[0].features.map((feat, idx) => {
            return { id: idx, name: feat }
          })
          this.tree_data = tree_data
          console.log(feats)
        })
      console.log(this.dataset, this.station)
    }
  }
}
</script>
