let L, theta0, g, t = 0;
let sliders = {};
let angle = 0, angularVelocity = 0;
let period;

function setup() {
  createCanvas(800, 500);
  L = 150; // in pixels
  theta0 = radians(30);
  g = 981; // in pixels/s^2
  period = 2 * PI * sqrt(L / g);
  sliders.length = createSlider(50, 300, 150, 1);
  sliders.angle = createSlider(0, 90, 30, 1);
  createP('Length: ');
  createP('Initial Angle: ');
  createButton('Reset').mousePressed(resetSimulation);
}

function draw() {
  background(0);
  drawAxes();
  L = sliders.length.value();
  theta0 = radians(sliders.angle.value());
  g = 981;
  period = 2 * PI * sqrt(L / g);
  updatePendulum();
  drawPendulum();
  displayValues();
  t += deltaTime / 1000;
}

function drawAxes() {
  stroke(128);
  line(0, height / 2, width, height / 2);
  line(width / 2, 0, width / 2, height);
}

function updatePendulum() {
  let angularAcceleration = -g / L * sin(angle);
  angularVelocity += angularAcceleration * deltaTime / 1000;
  angle += angularVelocity * deltaTime / 1000;
}

function drawPendulum() {
  let x = width / 2 + L * sin(angle);
  let y = height / 2 - L * cos(angle);
  stroke(255);
  line(width / 2, height / 2, x, y);
  fill(255);
  ellipse(x, y, 10, 10);
}

function displayValues() {
  fill(255);
  noStroke();
  textSize(16);
  text('Period: ' + period.toFixed(2) + ' s', 10, 20);
  text('Angle: ' + degrees(angle).toFixed(2) + ' degrees', 10, 40);
  text('Angular Velocity: ' + angularVelocity.toFixed(2) + ' rad/s', 10, 60);
}

function resetSimulation() {
  angle = theta0;
  angularVelocity = 0;
  t = 0;
}