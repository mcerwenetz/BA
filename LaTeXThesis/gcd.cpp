int gcd(int x, int y) {  // greatest common divisor
    while (x != 0) {  // $x \not= 0$
        int h = x; // prepare swap
        x = y%x; 
        y = h;
    }
    return y;
}
