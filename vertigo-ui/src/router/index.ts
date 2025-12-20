import LoginView from "@/views/LoginView.vue";
import SignupView from "@/views/SignupView.vue";
import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      redirect: "/login",
      name: "Default",
      meta: {
        requiresAuth: false,
      },
    },
    {
      path: "/dashboard",
      name: "Dashboard",
      component: () => import("@/views/DashboardView.vue"),
      meta: {
        requiresAuth: true,
        showHeaderItem: true,
      },
    },
    {
      path: "/settings",
      name: "Settings",
      component: () => import("@/views/SettingsView.vue"),
      meta: {
        requiresAuth: true,
        showHeaderItem: true,
      },
    },
    {
      path: "/collection",
      name: "Collection",
      component: () => import("@/views/CollectionView.vue"),
      meta: {
        requiresAuth: true,
        showHeaderItem: true,
      },
    },
    {
      path: "/wishlist",
      name: "Wishlist",
      component: () => import("@/views/WishlistView.vue"),
      meta: {
        requiresAuth: true,
        showHeaderItem: true,
      },
    },
    {
      path: "/about",
      name: "about",
      meta: {
        requiresAuth: true,
        showHeaderItem: true,
      },
      component: () => import("@/views/SeriesView.vue"),
    },
    {
      path: "/login",
      name: "Login",
      meta: {
        requiresAuth: false,
        showHeaderItem: false,
      },
      component: LoginView,
    },
    {
      path: "/register",
      name: "SignUp",
      component: SignupView,
      meta: {
        requiresAuth: false,
        showHeaderItem: false,
      },
    },
    {
      path: "/series/:Id-:Link",
      name: "SeriesDetail",
      meta: {
        requiresAuth: true,
        showHeaderItem: true,
        transparentHeader: true,
      },
      component: () => import("@/views/SeriesView.vue"),
    },
    {
      path: "/series/create",
      name: "AddSeries",
      meta: {
        requiresAuth: true,
        showHeaderItem: true,
      },
      component: () => import("@/views/AddSeriesView.vue"),
    },
    {
      path: "/series/edit/:Id-:Link",
      name: "EditSeries",
      meta: {
        requiresAuth: true,
        showHeaderItem: true,
      },
      component: () => import("@/views/EditSeriesView.vue"),
    },
    {
      path: "/publisher",
      name: "PublisherList",
      meta: {
        requiresAuth: true,
        showHeaderItem: true,
      },
      component: () => import("@/views/EntityListView.vue"),
      props: { type: "publisher" },
    },
    {
      path: "/publisher/create",
      name: "AddPublisher",
      meta: {
        requiresAuth: true,
        showHeaderItem: true,
      },
      component: () => import("@/views/EntityCreateView.vue"),
      props: { type: "publisher" },
    },
    {
      path: "/publisher/edit/:Id-:Link",
      name: "PublisherEdit",
      meta: {
        requiresAuth: true,
        showHeaderItem: true,
      },
      component: () => import("@/views/EntityEditView.vue"),
      props: { type: "publisher" },
    },
    {
      path: "/publisher/:Id-:Link",
      name: "PublisherDetail",
      meta: {
        requiresAuth: true,
        showHeaderItem: true,
      },
      component: () => import("@/views/EntityDetailView.vue"),
      props: { type: "publisher" },
    },
    {
      path: "/creator",
      name: "CreatorList",
      meta: {
        requiresAuth: true,
        showHeaderItem: true,
      },
      component: () => import("@/views/EntityListView.vue"),
      props: { type: "creator" },
    },
    {
      path: "/creator/create",
      name: "AddCreator",
      meta: {
        requiresAuth: true,
        showHeaderItem: true,
      },
      component: () => import("@/views/EntityCreateView.vue"),
      props: { type: "creator" },
    },
    {
      path: "/creator/:Id-:Link",
      name: "CreatorDetail",
      meta: {
        requiresAuth: true,
        showHeaderItem: true,
      },
      component: () => import("@/views/EntityDetailView.vue"),
      props: { type: "creator" },
    },
    {
      path: "/creator/edit/:Id-:Link",
      name: "CreatorEdit",
      meta: {
        requiresAuth: true,
        showHeaderItem: true,
      },
      component: () => import("@/views/EntityEditView.vue"),
      props: { type: "creator" },
    },
    {
      path: "/character",
      name: "CharacterList",
      meta: {
        requiresAuth: true,
        showHeaderItem: true,
      },
      component: () => import("@/views/EntityListView.vue"),
      props: { type: "character" },
    },
    {
      path: "/character/create",
      name: "AddCharacter",
      meta: {
        requiresAuth: true,
        showHeaderItem: true,
      },
      component: () => import("@/views/EntityCreateView.vue"),
      props: { type: "character" },
    },
    {
      path: "/character/:Id-:Link",
      name: "CharacterDetail",
      meta: {
        requiresAuth: true,
        showHeaderItem: true,
      },
      component: () => import("@/views/EntityDetailView.vue"),
      props: { type: "character" },
    },
    {
      path: "/character/edit/:Id-:Link",
      name: "CharacterEdit",
      meta: {
        requiresAuth: true,
        showHeaderItem: true,
      },
      component: () => import("@/views/EntityEditView.vue"),
      props: { type: "character" },
    },
    // {
    //   path: "/:type/:Id-:Link",
    //   name: "PublisherDetail",
    //   meta: {
    //     requiresAuth: true,
    //     showHeaderItem: true,
    //   },
    //   component: () =>
    //     import("@/views/entities/detail_views/PublisherView.vue"),
    // },
  ],
});

router.beforeEach((to, from, next) => {
  if (to.name === "Login") {
    localStorage.getItem("isUserLoggedIn")
      ? next({ name: "Dashboard" })
      : next();
    // next() // login route is always  okay (we could use the requires auth flag below). prevent a redirect loop
  } else if (to.meta && to.meta.requiresAuth === false) {
    next(); // requires auth is explicitly set to false
  } else if (localStorage.getItem("isUserLoggedIn")) {
    next(); // i'm logged in. carry on
  } else {
    next({ name: "Login" }); // always put your redirect as the default case
  }
});

export default router;
