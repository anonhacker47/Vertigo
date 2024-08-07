import { createRouter, createWebHistory } from "vue-router";
import DashboardView from "../views/DashboardView.vue";

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
      component: DashboardView,
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: "/collection",
      name: "Collection",
      component: () => import("../views/CollectionView.vue"),
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: "/wishlist",
      name: "Wishlist",
      component: () => import("../views/WishlistView.vue"),
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: "/about",
      name: "about",
      meta: {
        requiresAuth: true,
      },
      component: () => import("../views/SeriesView.vue"),
    },
    {
      path: "/login",
      name: "Login",
      meta: {
        requiresAuth: false,
      },
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import("../views/LoginView.vue"),
    },
    {
      path: "/register",
      name: "SignUp",
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import("../views/SignupView.vue"),
      meta: {
        requiresAuth: false,
      },
    },
    {
      path: "/series/:Id-:Link",
      name: "series",
      meta: {
        requiresAuth: true,
        removeHeader: true,
      },
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import("../views/SeriesView.vue"),
    },
    {
      path: "/add",
      name: "addnew",
      meta: {
        requiresAuth: true,
      },
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import("../views/AddNewView.vue"),
    },
  ],
});

router.beforeEach((to, from, next) => {
  if (to.name === "Login") {
    localStorage.getItem("isUserLoggedIn") ? next({ name: "Dashboard" }) : next();
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
