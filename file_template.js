function base64ToUint8Array(base64String) {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
  let result = [];

  for (let i = 0; i < base64String.length / 4; i++) {
    let chunk = [...base64String.slice(4 * i, 4 * i + 4)];
    let binary = chunk.map(char => chars.indexOf(char).toString(2).padStart(6, 0)).join('');
    let bytes = binary.match(/.{1,8}/g).map(byteStr => +('0b' + byteStr));
    result.push(...bytes.slice(0, 3 - (base64String[4 * i + 2] === "=") - (base64String[4 * i + 3] === "=")));
  }
  return new Uint8Array(result);
}

var iwadFileData = base64ToUint8Array("__iwad_file__");
var iwadFileName = "__iwad_filename__";
var wadFileData = base64ToUint8Array("__wad_file__");
var wadFileName = "__wad_filename__";

if (iwadFileData.length <= 9) {
  throw "Error: IWAD not found.";
}
if (wadFileData.length <= 9) {
  wadFileData = null;
}
else {
  Module.arguments = ["-file", wadFileName];
}

