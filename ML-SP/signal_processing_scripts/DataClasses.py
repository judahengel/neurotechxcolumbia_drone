import matplotlib.pyplot as plt
import mne


class Container:
    """Stores data to use with Plotter and MNE functions"""
    def __init__(self, sample_rate, n_channels, data, ch_names, lpass=None, hpass=None):
        """Container initialized with input parameters and processing parameters"""
        self.srate = sample_rate  # Sampling rate in Hz
        self.nchans = n_channels  # Number of channels
        self.ch_names = ch_names  # Names of channels
        self.data = data  # Data with shape (n_chans, n_samples)
        self.lpass = lpass  # Low pass frequency
        self.hpass = hpass  # High pass frequency
        self.mne_info = mne.create_info(self.ch_names, self.srate, 'eeg')
        self.processed_data = data

        self.ch_dct = dict(zip(ch_names, [x for x in range(n_channels)]))  # Converts channel names to indices

    def plot_raw(self, start, end, channel):
        """Plot of unprocessed data in given timeframe"""
        raw_mne = mne.io.RawArray(self.data.copy(), info=self.mne_info)
        time_slc = raw_mne.time_as_index([start, end])
        slc, times = raw_mne[channel, time_slc[0]:time_slc[1]]
        slc = slc[0]

        fig = plt.figure(figsize=(10, 2.5), constrained_layout=True)
        fig.suptitle("Raw Data", fontsize=16)
        ax = fig.add_axes([.1, .2, .85, .6])
        ax.set_ylabel('Potential (μV)')
        ax.set_xlabel('Time (s)')
        ax.plot(times, slc)

        yrng = max(slc)-min(slc)
        ybuff = .15

        ax.set(xlim=(times[0], times[-1]), ylim=(min(slc)-yrng*ybuff, max(slc)+yrng*ybuff))

        return fig

    def plot_processed(self, start, end, channel, lpass=15, hpass=30, eog=False):
        """Plot of processed data in given timeframe"""
        raw_mne = mne.io.RawArray(self.data.copy(), info=self.mne_info)
        raw_mne.filter(l_freq=lpass, h_freq=hpass)
        time_slc = raw_mne.time_as_index([start, end])
        slc, times = raw_mne[channel, time_slc[0]:time_slc[1]]
        slc = slc[0]

        fig = plt.figure(figsize=(10, 2.5), constrained_layout=True)
        fig.suptitle("Processed Data", fontsize=16)
        ax = fig.add_axes([.1, .2, .85, .6])
        ax.set_ylabel('Potential (μV)')
        ax.set_xlabel('Time (s)')
        ax.plot(times, slc)

        yrng = max(slc)-min(slc)
        ybuff = .15

        yrange = (min(slc)-yrng*ybuff, max(slc)+yrng*ybuff)
        ax.set(xlim=(times[0], times[-1]), ylim=yrange)
        self.processed_data = raw_mne

        if eog:
            self.mark_eog_events([channel], ax, yrange)

        return fig

    def mark_eog_events(self, eye_channel_names, ax, yrange):
        """Marks places where EOG events are detected in a particular plot"""
        eog_events = mne.preprocessing.find_eog_events(self.processed_data, ch_name=eye_channel_names)
        locations = eog_events[:, 0]/self.srate

        ax.vlines(locations, yrange[0], yrange[1], colors='r')

    def detect_eog_events(self, eye_channel_names, threshold=None):
        eog_events = mne.preprocessing.find_eog_events(self.processed_data, ch_name=eye_channel_names,
                                                       thresh=threshold)
        return eog_events[:, 0]/self.srate
