class Solution:
    def romanToInt(self, s: str) -> int:
        degerler = {
            "I": 1,
            "V": 5,
            "X": 10,
            "L": 50,
            "C": 100,
            "D": 500,
            "M": 1000
        }

        toplam = 0

        for i in range(len(s)):
            if i + 1 < len(s) and degerler[s[i]] < degerler[s[i + 1]]:
                toplam -= degerler[s[i]]
            else:
                toplam += degerler[s[i]]

        return toplam