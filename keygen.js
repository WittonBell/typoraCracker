function randomSerial() {
    var $chars = 'L23456789ABCDEFGHJKMNPQRSTUVWXYZ';
    var maxPos = $chars.length;
    var serial = '';
    for (i = 0; i < 22; i++) {
        serial += $chars.charAt(Math.floor(Math.random() * maxPos));
    }
    serial += (e => {
        for (var t = "", i = 0; i < 2; i++) {
            for (var a = 0, s = 0; s < 16; s += 2) a += $chars.indexOf(e[i + s]);
            t += $chars[a %= $chars.length]
        }
        return t
    })(serial)
    return serial.slice(0, 6) + "-" + serial.slice(6, 12) + "-" + serial.slice(12, 18) + "-" + serial.slice(18, 24);
}
console.log(randomSerial());
