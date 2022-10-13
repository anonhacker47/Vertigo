import Api from "@/services/Api";

export default {
  getcards(token,orderby,orderdir) {
    return Api().get(`feed?orderby=${orderby}&orderdir=${orderdir}`,token);
    ;
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
