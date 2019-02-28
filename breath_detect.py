import numpy as np
import scipy as sp
import matplotlib.pyplot as plt

FFT_LEN = 512
FFT_LEN_2 = 256
SPS = 5
BUFF_LEN = 300*4
MU_SPEC_LEN_2 = 24
class BreathDetector:

    def __init__(self):
        self.buff_len = 0
        self.buff = np.zeros(BUFF_LEN)
        self.spec = np.reshape(np.zeros(BUFF_LEN*FFT_LEN), newshape=(BUFF_LEN, FFT_LEN))
        self.mu_spec = np.reshape(np.zeros(BUFF_LEN*FFT_LEN), newshape=(BUFF_LEN, FFT_LEN))


    def update(self, data):
        # update buff 更新数据缓冲，如果数据断开的话，需要重置，这里未设置
        if self.buff_len == BUFF_LEN:
            self.buff[:-len(data)] = self.buff[len(data):]
            self.buff[self.buff_len-len(data):] = data

            # update spec
            self.spec[:-len(data)] = self.spec[len(data):]

            # compute fft of incoming points 逐点计算新数据的频谱
            for m in range(len(data)+FFT_LEN_2-2):
                fft_data = np.zeros(FFT_LEN)
                idx = self.buff_len-FFT_LEN_2 - len(data)+m
                if (idx > self.buff_len-FFT_LEN_2):
                    fft_data[:FFT_LEN_2+self.buff_len-idx] = self.buff[idx-FFT_LEN_2:]
                else:
                    fft_data = self.buff[idx-FFT_LEN_2:idx+FFT_LEN_2]

                # print(idx, '1200', m)
                self.spec[idx] = np.abs(np.fft.fft(fft_data))
        else:
            self.buff[self.buff_len:self.buff_len+len(data)] = data


            buff_len = self.buff_len + len(data)

            # compute fft of incoming points 逐点计算新数据的频谱
            for m in range(len(data)):
                fft_data = np.zeros(FFT_LEN)
                idx = buff_len-len(data)+m
                if idx < FFT_LEN_2:
                    if buff_len < FFT_LEN_2:
                        fft_data[FFT_LEN_2-idx:FFT_LEN_2-idx+buff_len] = self.buff[:buff_len]
                    else:
                        fft_data[FFT_LEN_2-idx:] = self.buff[:idx+FFT_LEN_2]


                elif idx > buff_len - FFT_LEN_2:
                    if buff_len < FFT_LEN_2:
                        fft_data[:buff_len] = self.buff[:buff_len]
                    else:
                        fft_data[:buff_len-idx+FFT_LEN_2] = self.buff[idx-FFT_LEN_2:buff_len]

                else:
                    fft_data = self.buff[idx-FFT_LEN_2:idx+FFT_LEN_2]

                self.spec[idx] = np.abs(np.fft.fft(fft_data))

            # update buff_len
            self.buff_len += len(data)


        # update mu in a complete way 整个序列全部做一次频谱的平均
        for m in range(BUFF_LEN):
            if m > BUFF_LEN:
                break

            if m < MU_SPEC_LEN_2:
                self.mu_spec[m] = np.mean(self.spec[:m+MU_SPEC_LEN_2], axis=0)
            elif m > BUFF_LEN - MU_SPEC_LEN_2:
                self.mu_spec[m] = np.mean(self.spec[m-MU_SPEC_LEN_2:], axis=0)
            else:
                self.mu_spec[m] = np.mean(self.spec[m-MU_SPEC_LEN_2:m+MU_SPEC_LEN_2], axis=0)


    def detect(self, data):
        self.update(data)

        # predict br
        br = np.ones(len(data)) * -1
        for m in range(len(data)):
            br[m] = self._predict_breath(self.mu_spec[m])

        return br

    def _predict_breath(self, spec):

        # moving average of spec 做频谱的窗口平滑
        avg_len = 6
        avg_len_2 = 3
        avg = np.zeros(FFT_LEN+avg_len)
        avg[:avg_len_2] = spec[0]
        avg[avg_len_2:FFT_LEN+avg_len_2] = spec
        avg[FFT_LEN+avg_len_2:] = spec[-1]

        mu_spec = np.zeros(FFT_LEN)
        for m in range(FFT_LEN):
            mu_spec[m] = np.mean(avg[m:m+avg_len])

        # 找频谱上所有的峰值
        cnt = 0
        peak_len = 14
        search = np.arange(peak_len, FFT_LEN-peak_len)
        peak = []
        peakIdx = []
        for m in search:
            # 峰值搜索逻辑
            if (mu_spec[m] > mu_spec[m-1] and mu_spec[m] > mu_spec[m+1]
                    and mu_spec[m+1] > mu_spec[m+peak_len] and mu_spec[m-1] > mu_spec[m-peak_len]):
                cnt += 1
                peak.append(mu_spec[m])
                peakIdx.append(m)

        brPeak = -1
        brPeakIdx = -1


        # find the breath peak 呼吸主频的尖峰应当在5-50之内，并且能量值要大于4000，如果测试结果不理想，可以动态调整这两个数值
        for m in range(len(peak)):
            if peakIdx[m] < 50 and peakIdx[m] > 5 and peak[m] > 20000:
                brPeak = peak[m]
                brPeakIdx = peakIdx[m]
                break

        if brPeakIdx < 0:
            br = -1
        else:
            diffIdx = np.zeros(len(peak))
            for m in range(len(peakIdx)):
                diffIdx[m] = peakIdx[m] - brPeakIdx*2
                if diffIdx[m] > 0:
                    # found the side peak 找到主频的谐波旁瓣
                    sidePeak = peak[m]
                    sidePeakIdx = peakIdx[m]
                    break

            if sidePeakIdx < 0:
                br = -1
            else:
                if brPeak / sidePeak > 1.5: # 如果比值大于1.3，则认为该呼吸成分周期特征明显
                    br = brPeakIdx
                else:
                    br = -1

        return br




if __name__ == '__main__':
    bd = BreathDetector()
    for m in range(100):
        bd.detect(range(10))

