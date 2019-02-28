from breath_detect import BreathDetector
import matplotlib.pyplot as plt
data_breath = [int(str) for str in open('breath_test.txt').read().split(',')]
data_nobreath = [int(str) for str in open('nobreath_test.txt').read().split(',')]
# plt.plot(data_breath)
# plt.plot(data_nobreath)

detector = BreathDetector()

br = detector.detect(data_breath[:300])
print(br)
br = detector.detect(data_breath[300:600])
print(br)
br = detector.detect(data_breath[600:900])
print(br)
br = detector.detect(data_breath[900:1200])
print(br)


br = detector.detect(data_nobreath[:300])
print(br)
br = detector.detect(data_nobreath[300:600])
print(br)
br = detector.detect(data_nobreath[600:900])
print(br)
br = detector.detect(data_nobreath[900:1200])
print(br)

