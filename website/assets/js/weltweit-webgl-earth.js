/* Local WebGL2/1 renderer: no CDN, independent GPU sphere shading. */
(() => {
    'use strict';
    const host = document.getElementById('hammel-universe');
    if (!host)
        return;
    const layer = document.createElement('canvas');
    layer.id = 'hammel-webgl-earth';
    layer.setAttribute('aria-hidden', 'true');
    layer.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:1';
    host.parentNode.insertBefore(layer, host);
    const gl = layer.getContext('webgl', { alpha: true, antialias: true, premultipliedAlpha: false });
    if (!gl)
        return;
    const vs = `attribute vec2 a;varying vec2 uv;void main(){uv=a*.5+.5;gl_Position=vec4(a,0.,1.);}`;
    const fs = `precision highp float;varying vec2 uv;
uniform sampler2D earthTex;uniform sampler2D cloudTex;uniform sampler2D lightsTex;
uniform vec2 res,center;uniform float radius,longitude,latitude,t,opacity;
const float PI=3.141592653589793;
void main(){
 vec2 pos=vec2(uv.x*res.x,(1.-uv.y)*res.y);vec2 p=(pos-center)/radius;
 float d=dot(p,p);
 if(d>1.18){discard;}
 float edge=sqrt(max(0.,1.-d));
 if(d>=1.){
  float halo=exp(-pow((sqrt(d)-1.)*radius/9.,2.));
  gl_FragColor=vec4(vec3(.09,.30,.54)*halo,halo*.18*opacity);return;
 }
 vec3 n=vec3(p.x,-p.y,edge);
 float ct=cos(latitude),st=sin(latitude);
 vec3 v=vec3(n.x,n.y*ct+n.z*st,-n.y*st+n.z*ct);
 float lon=atan(v.x,v.z)+longitude;
 float lat=asin(clamp(v.y,-1.,1.));
 vec2 texuv=vec2(fract(lon/(2.*PI)+.5),.5-lat/PI);
 vec3 ground=texture2D(earthTex,texuv).rgb;
 float city=texture2D(lightsTex,texuv).r;
 vec3 sun=normalize(vec3(-.68,.20,.70));
 float sunlight=dot(n,sun);
 float day=smoothstep(-.24,.43,sunlight);
 float diffuse=max(sunlight,0.);
 float land=clamp((ground.r-ground.b*.65+.03)*2.8,0.,1.);
 // Every continent stays visible: polished midnight charcoal with amber city networks.
 vec3 midnight=mix(vec3(.004,.012,.030),vec3(.074,.068,.067),land);
 vec3 warmTerrain=mix(vec3(.010,.021,.041),vec3(.16,.115,.077),land);
 vec3 color=mix(midnight,warmTerrain,day*.72);
 // A subdued hint of real geography without the familiar bright satellite-map appearance.
 color+=ground*(.055+.19*day*diffuse);
 // Emissive warm metropolis texture visible on the whole globe.
 float urban=pow(city,.82);
 vec3 amber=vec3(1.0,.52,.17);
 color+=amber*urban*(1.35-.25*day);
 // Glowing fine metropolitan halos, while city centers stay crisp.
 color+=vec3(.55,.18,.035)*pow(urban,.48)*.16;
 // Soft high-altitude cloud wisps and a directional film-grade atmosphere.
 float cloud=texture2D(cloudTex,vec2(fract(texuv.x+t*.0000018),texuv.y)).r;
 cloud=smoothstep(.57,.88,cloud);
 color=mix(color,vec3(.30,.34,.39),cloud*(.035+.095*day));
 float rim=pow(1.-edge,6.);
 color+=vec3(.10,.25,.46)*rim*(.18+.24*day);
 float sunrise=pow(1.-edge,18.)*pow(max(sunlight,0.),4.);
 color+=vec3(1.,.49,.17)*sunrise*.75;
 float alpha=opacity;
 gl_FragColor=vec4(color,alpha);
}`;
    function shader(type, source) { let s = gl.createShader(type); gl.shaderSource(s, source); gl.compileShader(s); if (!gl.getShaderParameter(s, gl.COMPILE_STATUS))
        throw Error(gl.getShaderInfoLog(s)); return s; }
    let program;
    try {
        program = gl.createProgram();
        gl.attachShader(program, shader(gl.VERTEX_SHADER, vs));
        gl.attachShader(program, shader(gl.FRAGMENT_SHADER, fs));
        gl.linkProgram(program);
        if (!gl.getProgramParameter(program, gl.LINK_STATUS))
            throw Error(gl.getProgramInfoLog(program));
    }
    catch (e) {
        console.warn('HAMMEL WebGL unavailable', e);
        layer.remove();
        return;
    }
    gl.useProgram(program);
    let buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, 1]), gl.STATIC_DRAW);
    let a = gl.getAttribLocation(program, 'a');
    gl.enableVertexAttribArray(a);
    gl.vertexAttribPointer(a, 2, gl.FLOAT, false, 0, 0);
    const U = {};
    for (const k of ['res', 'center', 'radius', 'longitude', 'latitude', 't', 'opacity'])
        U[k] = gl.getUniformLocation(program, k);
    const textures = [];
    let ready = 0;
    function loadTexture(path, unit) { const img = new Image(); img.onload = () => { const tex = gl.createTexture(); gl.activeTexture(gl.TEXTURE0 + unit); gl.bindTexture(gl.TEXTURE_2D, tex); gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, false); gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, img); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.REPEAT); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR); textures[unit] = tex; ready++; }; img.onerror = () => console.warn('HAMMEL texture missing', path); img.src = path; }
    loadTexture('../assets/img/earth-blue-marble.jpg', 0);
    loadTexture('../assets/img/earth-clouds-cinematic.png', 1);
    loadTexture('../assets/img/earth-night-lights-wow.png', 2);
    gl.uniform1i(gl.getUniformLocation(program, 'earthTex'), 0);
    gl.uniform1i(gl.getUniformLocation(program, 'cloudTex'), 1);
    gl.uniform1i(gl.getUniformLocation(program, 'lightsTex'), 2);
    window.hammelWebGLEarth = { render(cx, cy, r, longitude, latitude, opacity, phase) {
            if (ready !== 3) {
                layer.style.opacity = '0';
                return false;
            }
            layer.style.opacity = '1';
            const dpr = Math.min(window.devicePixelRatio || 1, 2), w = host.clientWidth, h = host.clientHeight;
            if (layer.width !== Math.round(w * dpr) || layer.height !== Math.round(h * dpr)) {
                layer.width = Math.round(w * dpr);
                layer.height = Math.round(h * dpr);
                gl.viewport(0, 0, layer.width, layer.height);
            }
            gl.useProgram(program);
            gl.uniform2f(U.res, layer.width, layer.height);
            gl.uniform2f(U.center, cx * dpr, cy * dpr);
            gl.uniform1f(U.radius, r * dpr);
            gl.uniform1f(U.longitude, longitude);
            gl.uniform1f(U.latitude, latitude);
            gl.uniform1f(U.opacity, opacity);
            gl.uniform1f(U.t, phase);
            gl.enable(gl.BLEND);
            gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
            gl.clearColor(0, 0, 0, 0);
            gl.clear(gl.COLOR_BUFFER_BIT);
            gl.drawArrays(gl.TRIANGLES, 0, 6);
            return true;
        } };
})();
