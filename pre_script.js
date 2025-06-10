var Module = {};
var consoleLines = [];
var jsFramebuffer = [];
var pressedKeys = {};
var keyInputQueue = [];

function printConsoleMessage(message) {
  consoleLines.push(message);
  if (consoleLines.length > 25) 
    consoleLines.shift();
  
  for (var i = 0; i < consoleLines.length; i++) {
    var row = consoleLines[i];
    globalThis.getField("console_" + (25 - i - 1)).value = row;
  }
}

Module.print = function(message) {
  let maxLength = 80;
  let numLines = Math.ceil(message.length / maxLength);
  
  for (let i = 0, offset = 0; i < numLines; ++i, offset += maxLength) {
    printConsoleMessage(message.substr(offset, maxLength));
  }
}
Module.printErr = function(message) {
  printConsoleMessage(message);
}

function handleKeyPress(keyString) {
  if ("WASD".includes(keyString)) {
    keyString = keyString.toLowerCase();
    handleKeyPress("_");
  }
  let keyCode = keyString.charCodeAt(0);
  let doomKey = _key_to_doomkey(keyCode);
  printConsoleMessage("pressed: " + keyString + " " + keyCode + " ");
  if (doomKey === -1) 
    return;

  pressedKeys[doomKey] = 2;
}

function handleKeyDown(keyString) {
  let keyCode = keyString.charCodeAt(0);
  let doomKey = _key_to_doomkey(keyCode);
  printConsoleMessage("key down: " + keyString + " " + keyCode + " ");
  if (doomKey === -1) 
    return;
  pressedKeys[doomKey] = 1;
}

function handleKeyUp(keyString) {
  let keyCode = keyString.charCodeAt(0);
  let doomKey = _key_to_doomkey(keyCode);
  printConsoleMessage("key up: " + keyString + " " + keyCode + " ");
  if (doomKey === -1) 
    return;
  pressedKeys[doomKey] = 0;
}

function resetInputBox() {
  globalThis.getField("key_input").value = "Type here for keyboard controls.";
}
app.setInterval("resetInputBox()", 1000);

function writeToFile(filename, data) {
  let stream = FS.open("/" + filename, "w+");
  FS.write(stream, data, 0, data.length, 0);
  FS.close(stream);
}

function createFramebuffer(width, height) {
  jsFramebuffer = [];
  for (let y = 0; y < height; y++) {
    let row = Array(width);
    for (let x = 0; x < width; x++) {
      row[x] = "_";
    }
    jsFramebuffer.push(row);
  }
}

function updateFramebuffer(framebufferPtr, framebufferLength, width, height) {
  let framebuffer = Module.HEAPU8.subarray(framebufferPtr, framebufferPtr + framebufferLength);
  for (let y = 0; y < height; y++) {
    let row = jsFramebuffer[y];
    let oldRow = row.join("");
    for (let x = 0; x < width; x++) {
      let index = (y * width + x) * 4;
      let r = framebuffer[index];
      let g = framebuffer[index + 1];
      let b = framebuffer[index + 2];
      let avg = (r + g + b) / 3;

      if (avg > 200)
        row[x] = "_";
      else if (avg > 150)
        row[x] = "::";
      else if (avg > 100)
        row[x] = "?";
      else if (avg > 50)
        row[x] = "//";
      else if (avg > 25)
        row[x] = "b";
      else
        row[x] = "#";
    }
    let rowString = row.join("");
    if (rowString !== oldRow)
      globalThis.getField("field_" + (height - y - 1)).value = rowString;
  }
}

