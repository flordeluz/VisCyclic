<template>
  <v-app>
    <v-app-bar color="primary" app clipped-left>
      <v-toolbar-title class="white--text"> <h1>VisCyclic</h1></v-toolbar-title>

      <v-spacer></v-spacer>
      <v-btn class="mr-2" router to="/metadata" outlined color="white"
        >Home</v-btn
      >

      <v-btn router to="spiral" outlined color="white">Spiral</v-btn>
    </v-app-bar>

    <v-navigation-drawer v-model="showSidebar" temporary fixed>
      <v-list nav>
        <v-list-item>
          <v-list-item-content class="my-2">
            <h1>VisWeb</h1>
          </v-list-item-content>
        </v-list-item>
        <v-divider></v-divider>

        <v-list-item-group ripple="true" class="mt-5">
          <v-list-item>
            <v-list-item-icon>
              <v-icon>mdi-theme-light-dark</v-icon>
            </v-list-item-icon>
            <v-list-item-title text @click="changeTheme"
              >Modo {{ this.darkMode ? 'claro' : 'oscuro' }}</v-list-item-title
            >
          </v-list-item>
        </v-list-item-group>
      </v-list>
    </v-navigation-drawer>
    <v-main>
      <router-view></router-view>
    </v-main>
  </v-app>
</template>

<script>
export default {
  name: 'App',

  components: {},

  data: () => ({
    //
    darkMode: false,
    showSidebar: null,
    openModal: false,
    searchData: '',
    mode: 'ts'
  }),

  computed: {},
  mounted: function() {
    this.$router.push('/spiral')
  },

  methods: {
    changeTheme: function() {
      this.darkMode = !this.darkMode
      this.$vuetify.theme.dark = this.darkMode
      localStorage.setItem('darkMode', this.darkMode)
      console.log('Changing to', this.darkMode, this.$vuetify.theme.dark)
    },
    changeView: function() {
      //   if (this.mode == 'ts') {
      //     this.$router.go('/spiral')
      //     this.mode = 'spiral'
      //     return
      //   } else {
      //     this.$router.go('/')
      //     this.mode = 'ts'
      //     return
      //   }
      // }
    }
  }
}
</script>
