import Api from "@/services/Api";

export default {
  getcards(token) {
    return Api().get("feed",token);
  },
  addpost(data,headers) {
    return Api().post("posts",data,headers
      );
  },
  removepost(data,headers) {
    return Api().delete(`posts/${data}`,headers
      );
  },
};
