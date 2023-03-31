import{f as W,r as cr,o as dr,a as hr,b as ue,d as B,w as pr}from"./index.109f29c0.js";import{a as mr}from"./_commonjsHelpers.0cb936ab.js";var Ve={exports:{}},le={exports:{}},Je=function(r,t){return function(){for(var n=new Array(arguments.length),a=0;a<n.length;a++)n[a]=arguments[a];return r.apply(t,n)}},vr=Je,ce=Object.prototype.toString,de=function(e){return function(r){var t=ce.call(r);return e[t]||(e[t]=t.slice(8,-1).toLowerCase())}}(Object.create(null));function x(e){return e=e.toLowerCase(),function(t){return de(t)===e}}function he(e){return Array.isArray(e)}function $(e){return typeof e>"u"}function Er(e){return e!==null&&!$(e)&&e.constructor!==null&&!$(e.constructor)&&typeof e.constructor.isBuffer=="function"&&e.constructor.isBuffer(e)}var We=x("ArrayBuffer");function yr(e){var r;return typeof ArrayBuffer<"u"&&ArrayBuffer.isView?r=ArrayBuffer.isView(e):r=e&&e.buffer&&We(e.buffer),r}function Rr(e){return typeof e=="string"}function wr(e){return typeof e=="number"}function ze(e){return e!==null&&typeof e=="object"}function L(e){if(de(e)!=="object")return!1;var r=Object.getPrototypeOf(e);return r===null||r===Object.prototype}var br=x("Date"),Or=x("File"),xr=x("Blob"),Ar=x("FileList");function pe(e){return ce.call(e)==="[object Function]"}function _r(e){return ze(e)&&pe(e.pipe)}function Sr(e){var r="[object FormData]";return e&&(typeof FormData=="function"&&e instanceof FormData||ce.call(e)===r||pe(e.toString)&&e.toString()===r)}var Cr=x("URLSearchParams");function Pr(e){return e.trim?e.trim():e.replace(/^\s+|\s+$/g,"")}function Tr(){return typeof navigator<"u"&&(navigator.product==="ReactNative"||navigator.product==="NativeScript"||navigator.product==="NS")?!1:typeof window<"u"&&typeof document<"u"}function me(e,r){if(!(e===null||typeof e>"u"))if(typeof e!="object"&&(e=[e]),he(e))for(var t=0,i=e.length;t<i;t++)r.call(null,e[t],t,e);else for(var n in e)Object.prototype.hasOwnProperty.call(e,n)&&r.call(null,e[n],n,e)}function fe(){var e={};function r(n,a){L(e[a])&&L(n)?e[a]=fe(e[a],n):L(n)?e[a]=fe({},n):he(n)?e[a]=n.slice():e[a]=n}for(var t=0,i=arguments.length;t<i;t++)me(arguments[t],r);return e}function gr(e,r,t){return me(r,function(n,a){t&&typeof n=="function"?e[a]=vr(n,t):e[a]=n}),e}function Nr(e){return e.charCodeAt(0)===65279&&(e=e.slice(1)),e}function Dr(e,r,t,i){e.prototype=Object.create(r.prototype,i),e.prototype.constructor=e,t&&Object.assign(e.prototype,t)}function qr(e,r,t){var i,n,a,s={};r=r||{};do{for(i=Object.getOwnPropertyNames(e),n=i.length;n-- >0;)a=i[n],s[a]||(r[a]=e[a],s[a]=!0);e=Object.getPrototypeOf(e)}while(e&&(!t||t(e,r))&&e!==Object.prototype);return r}function Ur(e,r,t){e=String(e),(t===void 0||t>e.length)&&(t=e.length),t-=r.length;var i=e.indexOf(r,t);return i!==-1&&i===t}function Br(e){if(!e)return null;var r=e.length;if($(r))return null;for(var t=new Array(r);r-- >0;)t[r]=e[r];return t}var Lr=function(e){return function(r){return e&&r instanceof e}}(typeof Uint8Array<"u"&&Object.getPrototypeOf(Uint8Array)),m={isArray:he,isArrayBuffer:We,isBuffer:Er,isFormData:Sr,isArrayBufferView:yr,isString:Rr,isNumber:wr,isObject:ze,isPlainObject:L,isUndefined:$,isDate:br,isFile:Or,isBlob:xr,isFunction:pe,isStream:_r,isURLSearchParams:Cr,isStandardBrowserEnv:Tr,forEach:me,merge:fe,extend:gr,trim:Pr,stripBOM:Nr,inherits:Dr,toFlatObject:qr,kindOf:de,kindOfTest:x,endsWith:Ur,toArray:Br,isTypedArray:Lr,isFileList:Ar},C=m;function be(e){return encodeURIComponent(e).replace(/%3A/gi,":").replace(/%24/g,"$").replace(/%2C/gi,",").replace(/%20/g,"+").replace(/%5B/gi,"[").replace(/%5D/gi,"]")}var Xe=function(r,t,i){if(!t)return r;var n;if(i)n=i(t);else if(C.isURLSearchParams(t))n=t.toString();else{var a=[];C.forEach(t,function(f,d){f===null||typeof f>"u"||(C.isArray(f)?d=d+"[]":f=[f],C.forEach(f,function(h){C.isDate(h)?h=h.toISOString():C.isObject(h)&&(h=JSON.stringify(h)),a.push(be(d)+"="+be(h))}))}),n=a.join("&")}if(n){var s=r.indexOf("#");s!==-1&&(r=r.slice(0,s)),r+=(r.indexOf("?")===-1?"?":"&")+n}return r},Fr=m;function j(){this.handlers=[]}j.prototype.use=function(r,t,i){return this.handlers.push({fulfilled:r,rejected:t,synchronous:i?i.synchronous:!1,runWhen:i?i.runWhen:null}),this.handlers.length-1};j.prototype.eject=function(r){this.handlers[r]&&(this.handlers[r]=null)};j.prototype.forEach=function(r){Fr.forEach(this.handlers,function(i){i!==null&&r(i)})};var $r=j,jr=m,Ir=function(r,t){jr.forEach(r,function(n,a){a!==t&&a.toUpperCase()===t.toUpperCase()&&(r[t]=n,delete r[a])})},Ke=m;function T(e,r,t,i,n){Error.call(this),this.message=e,this.name="AxiosError",r&&(this.code=r),t&&(this.config=t),i&&(this.request=i),n&&(this.response=n)}Ke.inherits(T,Error,{toJSON:function(){return{message:this.message,name:this.name,description:this.description,number:this.number,fileName:this.fileName,lineNumber:this.lineNumber,columnNumber:this.columnNumber,stack:this.stack,config:this.config,code:this.code,status:this.response&&this.response.status?this.response.status:null}}});var Qe=T.prototype,Ye={};["ERR_BAD_OPTION_VALUE","ERR_BAD_OPTION","ECONNABORTED","ETIMEDOUT","ERR_NETWORK","ERR_FR_TOO_MANY_REDIRECTS","ERR_DEPRECATED","ERR_BAD_RESPONSE","ERR_BAD_REQUEST","ERR_CANCELED"].forEach(function(e){Ye[e]={value:e}});Object.defineProperties(T,Ye);Object.defineProperty(Qe,"isAxiosError",{value:!0});T.from=function(e,r,t,i,n,a){var s=Object.create(Qe);return Ke.toFlatObject(e,s,function(f){return f!==Error.prototype}),T.call(s,e.message,r,t,i,n),s.name=e.name,a&&Object.assign(s,a),s};var N=T,Ge={silentJSONParsing:!0,forcedJSONParsing:!0,clarifyTimeoutError:!1},w=m;function kr(e,r){r=r||new FormData;var t=[];function i(a){return a===null?"":w.isDate(a)?a.toISOString():w.isArrayBuffer(a)||w.isTypedArray(a)?typeof Blob=="function"?new Blob([a]):Buffer.from(a):a}function n(a,s){if(w.isPlainObject(a)||w.isArray(a)){if(t.indexOf(a)!==-1)throw Error("Circular reference detected in "+s);t.push(a),w.forEach(a,function(f,d){if(!w.isUndefined(f)){var c=s?s+"."+d:d,h;if(f&&!s&&typeof f=="object"){if(w.endsWith(d,"{}"))f=JSON.stringify(f);else if(w.endsWith(d,"[]")&&(h=w.toArray(f))){h.forEach(function(u){!w.isUndefined(u)&&r.append(c,i(u))});return}}n(f,c)}}),t.pop()}else r.append(s,i(a))}return n(e),r}var Ze=kr,z,Oe;function Mr(){if(Oe)return z;Oe=1;var e=N;return z=function(t,i,n){var a=n.config.validateStatus;!n.status||!a||a(n.status)?t(n):i(new e("Request failed with status code "+n.status,[e.ERR_BAD_REQUEST,e.ERR_BAD_RESPONSE][Math.floor(n.status/100)-4],n.config,n.request,n))},z}var X,xe;function Hr(){if(xe)return X;xe=1;var e=m;return X=e.isStandardBrowserEnv()?function(){return{write:function(i,n,a,s,o,f){var d=[];d.push(i+"="+encodeURIComponent(n)),e.isNumber(a)&&d.push("expires="+new Date(a).toGMTString()),e.isString(s)&&d.push("path="+s),e.isString(o)&&d.push("domain="+o),f===!0&&d.push("secure"),document.cookie=d.join("; ")},read:function(i){var n=document.cookie.match(new RegExp("(^|;\\s*)("+i+")=([^;]*)"));return n?decodeURIComponent(n[3]):null},remove:function(i){this.write(i,"",Date.now()-864e5)}}}():function(){return{write:function(){},read:function(){return null},remove:function(){}}}(),X}var Vr=function(r){return/^([a-z][a-z\d+\-.]*:)?\/\//i.test(r)},Jr=function(r,t){return t?r.replace(/\/+$/,"")+"/"+t.replace(/^\/+/,""):r},Wr=Vr,zr=Jr,er=function(r,t){return r&&!Wr(t)?zr(r,t):t},K,Ae;function Xr(){if(Ae)return K;Ae=1;var e=m,r=["age","authorization","content-length","content-type","etag","expires","from","host","if-modified-since","if-unmodified-since","last-modified","location","max-forwards","proxy-authorization","referer","retry-after","user-agent"];return K=function(i){var n={},a,s,o;return i&&e.forEach(i.split(`
`),function(d){if(o=d.indexOf(":"),a=e.trim(d.substr(0,o)).toLowerCase(),s=e.trim(d.substr(o+1)),a){if(n[a]&&r.indexOf(a)>=0)return;a==="set-cookie"?n[a]=(n[a]?n[a]:[]).concat([s]):n[a]=n[a]?n[a]+", "+s:s}}),n},K}var Q,_e;function Kr(){if(_e)return Q;_e=1;var e=m;return Q=e.isStandardBrowserEnv()?function(){var t=/(msie|trident)/i.test(navigator.userAgent),i=document.createElement("a"),n;function a(s){var o=s;return t&&(i.setAttribute("href",o),o=i.href),i.setAttribute("href",o),{href:i.href,protocol:i.protocol?i.protocol.replace(/:$/,""):"",host:i.host,search:i.search?i.search.replace(/^\?/,""):"",hash:i.hash?i.hash.replace(/^#/,""):"",hostname:i.hostname,port:i.port,pathname:i.pathname.charAt(0)==="/"?i.pathname:"/"+i.pathname}}return n=a(window.location.href),function(o){var f=e.isString(o)?a(o):o;return f.protocol===n.protocol&&f.host===n.host}}():function(){return function(){return!0}}(),Q}var Y,Se;function I(){if(Se)return Y;Se=1;var e=N,r=m;function t(i){e.call(this,i==null?"canceled":i,e.ERR_CANCELED),this.name="CanceledError"}return r.inherits(t,e,{__CANCEL__:!0}),Y=t,Y}var G,Ce;function Qr(){return Ce||(Ce=1,G=function(r){var t=/^([-+\w]{1,25})(:?\/\/|:)/.exec(r);return t&&t[1]||""}),G}var Z,Pe;function Te(){if(Pe)return Z;Pe=1;var e=m,r=Mr(),t=Hr(),i=Xe,n=er,a=Xr(),s=Kr(),o=Ge,f=N,d=I(),c=Qr();return Z=function(u){return new Promise(function(or,A){var D=u.data,q=u.headers,U=u.responseType,_;function ye(){u.cancelToken&&u.cancelToken.unsubscribe(_),u.signal&&u.signal.removeEventListener("abort",_)}e.isFormData(D)&&e.isStandardBrowserEnv()&&delete q["Content-Type"];var l=new XMLHttpRequest;if(u.auth){var ur=u.auth.username||"",fr=u.auth.password?unescape(encodeURIComponent(u.auth.password)):"";q.Authorization="Basic "+btoa(ur+":"+fr)}var H=n(u.baseURL,u.url);l.open(u.method.toUpperCase(),i(H,u.params,u.paramsSerializer),!0),l.timeout=u.timeout;function Re(){if(!!l){var R="getAllResponseHeaders"in l?a(l.getAllResponseHeaders()):null,S=!U||U==="text"||U==="json"?l.responseText:l.response,O={data:S,status:l.status,statusText:l.statusText,headers:R,config:u,request:l};r(function(J){or(J),ye()},function(J){A(J),ye()},O),l=null}}if("onloadend"in l?l.onloadend=Re:l.onreadystatechange=function(){!l||l.readyState!==4||l.status===0&&!(l.responseURL&&l.responseURL.indexOf("file:")===0)||setTimeout(Re)},l.onabort=function(){!l||(A(new f("Request aborted",f.ECONNABORTED,u,l)),l=null)},l.onerror=function(){A(new f("Network Error",f.ERR_NETWORK,u,l,l)),l=null},l.ontimeout=function(){var S=u.timeout?"timeout of "+u.timeout+"ms exceeded":"timeout exceeded",O=u.transitional||o;u.timeoutErrorMessage&&(S=u.timeoutErrorMessage),A(new f(S,O.clarifyTimeoutError?f.ETIMEDOUT:f.ECONNABORTED,u,l)),l=null},e.isStandardBrowserEnv()){var we=(u.withCredentials||s(H))&&u.xsrfCookieName?t.read(u.xsrfCookieName):void 0;we&&(q[u.xsrfHeaderName]=we)}"setRequestHeader"in l&&e.forEach(q,function(S,O){typeof D>"u"&&O.toLowerCase()==="content-type"?delete q[O]:l.setRequestHeader(O,S)}),e.isUndefined(u.withCredentials)||(l.withCredentials=!!u.withCredentials),U&&U!=="json"&&(l.responseType=u.responseType),typeof u.onDownloadProgress=="function"&&l.addEventListener("progress",u.onDownloadProgress),typeof u.onUploadProgress=="function"&&l.upload&&l.upload.addEventListener("progress",u.onUploadProgress),(u.cancelToken||u.signal)&&(_=function(R){!l||(A(!R||R&&R.type?new d:R),l.abort(),l=null)},u.cancelToken&&u.cancelToken.subscribe(_),u.signal&&(u.signal.aborted?_():u.signal.addEventListener("abort",_))),D||(D=null);var V=c(H);if(V&&["http","https","file"].indexOf(V)===-1){A(new f("Unsupported protocol "+V+":",f.ERR_BAD_REQUEST,u));return}l.send(D)})},Z}var ee,ge;function Yr(){return ge||(ge=1,ee=null),ee}var p=m,Ne=Ir,De=N,Gr=Ge,Zr=Ze,et={"Content-Type":"application/x-www-form-urlencoded"};function qe(e,r){!p.isUndefined(e)&&p.isUndefined(e["Content-Type"])&&(e["Content-Type"]=r)}function rt(){var e;return(typeof XMLHttpRequest<"u"||typeof process<"u"&&Object.prototype.toString.call(process)==="[object process]")&&(e=Te()),e}function tt(e,r,t){if(p.isString(e))try{return(r||JSON.parse)(e),p.trim(e)}catch(i){if(i.name!=="SyntaxError")throw i}return(t||JSON.stringify)(e)}var k={transitional:Gr,adapter:rt(),transformRequest:[function(r,t){if(Ne(t,"Accept"),Ne(t,"Content-Type"),p.isFormData(r)||p.isArrayBuffer(r)||p.isBuffer(r)||p.isStream(r)||p.isFile(r)||p.isBlob(r))return r;if(p.isArrayBufferView(r))return r.buffer;if(p.isURLSearchParams(r))return qe(t,"application/x-www-form-urlencoded;charset=utf-8"),r.toString();var i=p.isObject(r),n=t&&t["Content-Type"],a;if((a=p.isFileList(r))||i&&n==="multipart/form-data"){var s=this.env&&this.env.FormData;return Zr(a?{"files[]":r}:r,s&&new s)}else if(i||n==="application/json")return qe(t,"application/json"),tt(r);return r}],transformResponse:[function(r){var t=this.transitional||k.transitional,i=t&&t.silentJSONParsing,n=t&&t.forcedJSONParsing,a=!i&&this.responseType==="json";if(a||n&&p.isString(r)&&r.length)try{return JSON.parse(r)}catch(s){if(a)throw s.name==="SyntaxError"?De.from(s,De.ERR_BAD_RESPONSE,this,null,this.response):s}return r}],timeout:0,xsrfCookieName:"XSRF-TOKEN",xsrfHeaderName:"X-XSRF-TOKEN",maxContentLength:-1,maxBodyLength:-1,env:{FormData:Yr()},validateStatus:function(r){return r>=200&&r<300},headers:{common:{Accept:"application/json, text/plain, */*"}}};p.forEach(["delete","get","head"],function(r){k.headers[r]={}});p.forEach(["post","put","patch"],function(r){k.headers[r]=p.merge(et)});var ve=k,nt=m,it=ve,at=function(r,t,i){var n=this||it;return nt.forEach(i,function(s){r=s.call(n,r,t)}),r},re,Ue;function rr(){return Ue||(Ue=1,re=function(r){return!!(r&&r.__CANCEL__)}),re}var Be=m,te=at,st=rr(),ot=ve,ut=I();function ne(e){if(e.cancelToken&&e.cancelToken.throwIfRequested(),e.signal&&e.signal.aborted)throw new ut}var ft=function(r){ne(r),r.headers=r.headers||{},r.data=te.call(r,r.data,r.headers,r.transformRequest),r.headers=Be.merge(r.headers.common||{},r.headers[r.method]||{},r.headers),Be.forEach(["delete","get","head","post","put","patch","common"],function(n){delete r.headers[n]});var t=r.adapter||ot.adapter;return t(r).then(function(n){return ne(r),n.data=te.call(r,n.data,n.headers,r.transformResponse),n},function(n){return st(n)||(ne(r),n&&n.response&&(n.response.data=te.call(r,n.response.data,n.response.headers,r.transformResponse))),Promise.reject(n)})},E=m,tr=function(r,t){t=t||{};var i={};function n(c,h){return E.isPlainObject(c)&&E.isPlainObject(h)?E.merge(c,h):E.isPlainObject(h)?E.merge({},h):E.isArray(h)?h.slice():h}function a(c){if(E.isUndefined(t[c])){if(!E.isUndefined(r[c]))return n(void 0,r[c])}else return n(r[c],t[c])}function s(c){if(!E.isUndefined(t[c]))return n(void 0,t[c])}function o(c){if(E.isUndefined(t[c])){if(!E.isUndefined(r[c]))return n(void 0,r[c])}else return n(void 0,t[c])}function f(c){if(c in t)return n(r[c],t[c]);if(c in r)return n(void 0,r[c])}var d={url:s,method:s,data:s,baseURL:o,transformRequest:o,transformResponse:o,paramsSerializer:o,timeout:o,timeoutMessage:o,withCredentials:o,adapter:o,responseType:o,xsrfCookieName:o,xsrfHeaderName:o,onUploadProgress:o,onDownloadProgress:o,decompress:o,maxContentLength:o,maxBodyLength:o,beforeRedirect:o,transport:o,httpAgent:o,httpsAgent:o,cancelToken:o,socketPath:o,responseEncoding:o,validateStatus:f};return E.forEach(Object.keys(r).concat(Object.keys(t)),function(h){var u=d[h]||a,y=u(h);E.isUndefined(y)&&u!==f||(i[h]=y)}),i},ie,Le;function nr(){return Le||(Le=1,ie={version:"0.27.2"}),ie}var lt=nr().version,b=N,Ee={};["object","boolean","number","function","string","symbol"].forEach(function(e,r){Ee[e]=function(i){return typeof i===e||"a"+(r<1?"n ":" ")+e}});var Fe={};Ee.transitional=function(r,t,i){function n(a,s){return"[Axios v"+lt+"] Transitional option '"+a+"'"+s+(i?". "+i:"")}return function(a,s,o){if(r===!1)throw new b(n(s," has been removed"+(t?" in "+t:"")),b.ERR_DEPRECATED);return t&&!Fe[s]&&(Fe[s]=!0,console.warn(n(s," has been deprecated since v"+t+" and will be removed in the near future"))),r?r(a,s,o):!0}};function ct(e,r,t){if(typeof e!="object")throw new b("options must be an object",b.ERR_BAD_OPTION_VALUE);for(var i=Object.keys(e),n=i.length;n-- >0;){var a=i[n],s=r[a];if(s){var o=e[a],f=o===void 0||s(o,a,e);if(f!==!0)throw new b("option "+a+" must be "+f,b.ERR_BAD_OPTION_VALUE);continue}if(t!==!0)throw new b("Unknown option "+a,b.ERR_BAD_OPTION)}}var dt={assertOptions:ct,validators:Ee},ir=m,ht=Xe,$e=$r,je=ft,M=tr,pt=er,ar=dt,P=ar.validators;function g(e){this.defaults=e,this.interceptors={request:new $e,response:new $e}}g.prototype.request=function(r,t){typeof r=="string"?(t=t||{},t.url=r):t=r||{},t=M(this.defaults,t),t.method?t.method=t.method.toLowerCase():this.defaults.method?t.method=this.defaults.method.toLowerCase():t.method="get";var i=t.transitional;i!==void 0&&ar.assertOptions(i,{silentJSONParsing:P.transitional(P.boolean),forcedJSONParsing:P.transitional(P.boolean),clarifyTimeoutError:P.transitional(P.boolean)},!1);var n=[],a=!0;this.interceptors.request.forEach(function(y){typeof y.runWhen=="function"&&y.runWhen(t)===!1||(a=a&&y.synchronous,n.unshift(y.fulfilled,y.rejected))});var s=[];this.interceptors.response.forEach(function(y){s.push(y.fulfilled,y.rejected)});var o;if(!a){var f=[je,void 0];for(Array.prototype.unshift.apply(f,n),f=f.concat(s),o=Promise.resolve(t);f.length;)o=o.then(f.shift(),f.shift());return o}for(var d=t;n.length;){var c=n.shift(),h=n.shift();try{d=c(d)}catch(u){h(u);break}}try{o=je(d)}catch(u){return Promise.reject(u)}for(;s.length;)o=o.then(s.shift(),s.shift());return o};g.prototype.getUri=function(r){r=M(this.defaults,r);var t=pt(r.baseURL,r.url);return ht(t,r.params,r.paramsSerializer)};ir.forEach(["delete","get","head","options"],function(r){g.prototype[r]=function(t,i){return this.request(M(i||{},{method:r,url:t,data:(i||{}).data}))}});ir.forEach(["post","put","patch"],function(r){function t(i){return function(a,s,o){return this.request(M(o||{},{method:r,headers:i?{"Content-Type":"multipart/form-data"}:{},url:a,data:s}))}}g.prototype[r]=t(),g.prototype[r+"Form"]=t(!0)});var mt=g,ae,Ie;function vt(){if(Ie)return ae;Ie=1;var e=I();function r(t){if(typeof t!="function")throw new TypeError("executor must be a function.");var i;this.promise=new Promise(function(s){i=s});var n=this;this.promise.then(function(a){if(!!n._listeners){var s,o=n._listeners.length;for(s=0;s<o;s++)n._listeners[s](a);n._listeners=null}}),this.promise.then=function(a){var s,o=new Promise(function(f){n.subscribe(f),s=f}).then(a);return o.cancel=function(){n.unsubscribe(s)},o},t(function(s){n.reason||(n.reason=new e(s),i(n.reason))})}return r.prototype.throwIfRequested=function(){if(this.reason)throw this.reason},r.prototype.subscribe=function(i){if(this.reason){i(this.reason);return}this._listeners?this._listeners.push(i):this._listeners=[i]},r.prototype.unsubscribe=function(i){if(!!this._listeners){var n=this._listeners.indexOf(i);n!==-1&&this._listeners.splice(n,1)}},r.source=function(){var i,n=new r(function(s){i=s});return{token:n,cancel:i}},ae=r,ae}var se,ke;function Et(){return ke||(ke=1,se=function(r){return function(i){return r.apply(null,i)}}),se}var oe,Me;function yt(){if(Me)return oe;Me=1;var e=m;return oe=function(t){return e.isObject(t)&&t.isAxiosError===!0},oe}var He=m,Rt=Je,F=mt,wt=tr,bt=ve;function sr(e){var r=new F(e),t=Rt(F.prototype.request,r);return He.extend(t,F.prototype,r),He.extend(t,r),t.create=function(n){return sr(wt(e,n))},t}var v=sr(bt);v.Axios=F;v.CanceledError=I();v.CancelToken=vt();v.isCancel=rr();v.VERSION=nr().version;v.toFormData=Ze;v.AxiosError=N;v.Cancel=v.CanceledError;v.all=function(r){return Promise.all(r)};v.spread=Et();v.isAxiosError=yt();le.exports=v;le.exports.default=v;(function(e){e.exports=le.exports})(Ve);const Ot=mr(Ve.exports),xt=()=>Ot.create({baseURL:"http://127.0.0.1:5000/api/"}),At={register(e){return xt().post("register",e)}};const _t={class:"flex flex-col items-center justify-center px-6 py-8 mx-auto md:h-screen lg:py-0"},St={class:"w-full bg-white rounded-lg shadow dark:border md:mt-0 sm:max-w-md xl:p-0 dark:bg-gray-800 dark:border-gray-700"},Ct={class:"p-6 space-y-4 md:space-y-6 sm:p-8"},Pt=ue("h1",{class:"text-xl font-bold leading-tight tracking-tight text-gray-900 md:text-2xl dark:text-white"}," Create your Vertigo Account ",-1),Nt={__name:"SignupView",setup(e){W(""),W(""),W("");async function r(t){const i=await At.register({username:t.username,email_id:t.email_id,password:t.password});console.log(i.data)}return(t,i)=>{const n=cr("FormKit");return dr(),hr("div",_t,[ue("div",St,[ue("div",Ct,[Pt,B(n,{type:"form","submit-label":"Sign up",onSubmit:r},{default:pr(()=>[B(n,{type:"text",name:"username",label:"Username",validation:"required"}),B(n,{type:"email",name:"email_id",label:"Email Address",validation:"required|email|",placeholder:"demo@company.com"}),B(n,{type:"password",name:"password",label:"Password",validation:"required"}),B(n,{type:"password",name:"password_confirm",label:"Confirm Password",validation:"required|confirm","validation-label":"Password confirmation"})]),_:1})])])])}}};export{Nt as default};