function initWorldWind() {
  const wwd = new WorldWind.WorldWindow("globeCanvas");

  // Add a few default layers.
  wwd.addLayer(new WorldWind.BMNGLayer());
  wwd.addLayer(new WorldWind.BMNGLandsatLayer());
  wwd.addLayer(new WorldWind.AtmosphereLayer());
  wwd.addLayer(new WorldWind.CompassLayer());
  wwd.addLayer(new WorldWind.CoordinatesDisplayLayer(wwd));
  wwd.addLayer(new WorldWind.ViewControlsLayer(wwd));

  // Start over Madrid, Spain.
  wwd.navigator.lookAtLocation.latitude = 40.4168;
  wwd.navigator.lookAtLocation.longitude = -3.7038;
  wwd.navigator.range = 7e6;
}

function loadWorldWindWithFallback(urls, index = 0) {
  if (index >= urls.length) {
    const title = document.querySelector(".title");
    title.textContent = "Error: WorldWind could not be loaded from any source.";
    return;
  }

  const script = document.createElement("script");
  script.src = urls[index];
  script.async = true;

  script.onload = () => {
    if (typeof WorldWind === "undefined") {
      loadWorldWindWithFallback(urls, index + 1);
      return;
    }
    initWorldWind();
  };

  script.onerror = () => loadWorldWindWithFallback(urls, index + 1);
  document.head.appendChild(script);
}

loadWorldWindWithFallback([
  "https://files.worldwind.arc.nasa.gov/artifactory/web/0.11.0/worldwind.min.js",
  "https://cdn.jsdelivr.net/npm/@nasaworldwind/worldwind@0.11.0/build/dist/worldwind.min.js",
  "https://unpkg.com/@nasaworldwind/worldwind@0.11.0/build/dist/worldwind.min.js"
]);
