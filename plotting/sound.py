import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import matplotlib.ticker as tkr
import numpy as np
import pint
import seawater
from flask_babel import gettext

import plotting.utils as utils
from plotting.ts import TemperatureSalinityPlotter


class SoundSpeedPlotter(TemperatureSalinityPlotter):

    def __init__(self, dataset_name: str, query: str, **kwargs):
        self.plottype: str = "sound"

        super(
            SoundSpeedPlotter, self).__init__(dataset_name, query,
                                              **kwargs)

    def load_data(self):
        super(SoundSpeedPlotter, self).load_data()

        self.pressure = [seawater.pres(self.temperature_depths[idx], ll[0])
                         for idx, ll in enumerate(self.points)]

        ureg = pint.UnitRegistry()
        try:
            u = ureg.parse_units(self.variable_units[0].lower())
        except:
            u = ureg.dimensionless

        if u == ureg.boltzmann_constant:
            u = ureg.kelvin

        if u == ureg.kelvin:
            temperature_c = ureg.Quantity(
                self.temperature, u).to(ureg.celsius).magnitude
        else:
            temperature_c = self.temperature

        self.sspeed = seawater.svel(
            self.salinity, temperature_c, self.pressure
        )

    def plot(self):
        
        # Create base figure
        fig = plt.figure(figsize=self.figuresize, dpi=self.dpi)

        # Setup figure layout
        width = 2 if self.showmap else 1
        # Scale TS Diagram to be double the size of location map
        width_ratios = [1, 3] if self.showmap else None

        # Create layout helper
        gs = gridspec.GridSpec(1, width, width_ratios=width_ratios)

        
        # Plot Sound Speed profile
        plt.subplot(gs[:, 1 if self.showmap else 0])
        ax = plt.gca()
        i = 0
        colors = list()
        for i, ss in enumerate(self.sspeed):
            ax.plot(ss, self.temperature_depths[i], '-')
        
        for line in ax.get_lines():
            colors.append(line.get_color())

        # Render point location
        if self.showmap:
            plt.subplot(gs[0, 0])
            utils.point_plot(np.array([[x[0] for x in self.points],  # Latitudes
                                       [x[1] for x in self.points]]),
                                        colors=colors)  # Longitudes


        minspeed = np.amin(self.sspeed)
        maxspeed = np.amax(self.sspeed)
        
        
        if 'xscale' in self.query:
            ax.set_xlim([float(self.query.get('xscale')[0]),float(self.query.get('xscale')[1])])
        else:
            ax.set_xlim([
                np.amin(self.sspeed) - (maxspeed - minspeed) * 0.1,
                np.amax(self.sspeed) + (maxspeed - minspeed) * 0.1,
            ])


        if self.query.get('annotate'):
            # SOUND SPEED MINIMA
            
            minpos = np.where(self.sspeed[0] == minspeed)

            # SONIC LAYER DEPTH

            # Calculate
            soniclayerdepth_value = self.sspeed[0][0:int(minpos[0])].max()
            soniclayerdepth_idx = np.where(self.sspeed[0] == soniclayerdepth_value)
            soniclayerdepth = self.temperature_depths.data[0][soniclayerdepth_idx][0]

            soniclayerdepth_value = float("{0:.2f}".format(soniclayerdepth_value))

            # Plot and label
            plt.annotate('Sonic Layer Depth', (soniclayerdepth_value + 2, soniclayerdepth))
            plt.annotate(str(soniclayerdepth) + 'm', (soniclayerdepth_value + 4,soniclayerdepth + 2), textcoords="offset points",
            xytext=(0,10), ha='center')
            ax.axvline(x=soniclayerdepth_value, linestyle='--')
            # ~~~~~~~~~~~~~~~~~


            # CRITICAL DEPTH

            subset = self.sspeed[0][int(minpos[0]):]
            if subset.max() >= soniclayerdepth_value:
                criticaldepth_idx = (np.abs(subset - soniclayerdepth_value)).argmin()
                criticaldepth = self.temperature_depths.data[0][int(criticaldepth_idx) + int(minpos[0])]
                criticaldepth_value = subset[criticaldepth_idx]

                # Perform linear interpolation to get more accurate depth
                if (criticaldepth_value > soniclayerdepth_value):
                # Must also consider the previous value 
                    criticaldepth_sec_value = subset[criticaldepth_idx - 1]
                    criticaldepth_sec = self.temperature_depths.data[0][int(criticaldepth_idx - 1) + int(minpos[0])]
                    criticaldepth_true = criticaldepth_sec + (soniclayerdepth_value - criticaldepth_sec_value) * (criticaldepth - criticaldepth_sec) / (criticaldepth_value - criticaldepth_sec_value)

                else:
                # Must also consider the next value
                    criticaldepth_sec_value = subset[criticaldepth_idx + 1]
                    criticaldepth_sec = self.temperature_depths.data[0][int(criticaldepth_idx + 1) + int(minpos[0])]
                    criticaldepth_true = criticaldepth + (soniclayerdepth_value - criticaldepth_value) * (criticaldepth_sec - criticaldepth) / (criticaldepth_sec_value - criticaldepth_value)

                ax.hlines(y=criticaldepth_true,xmin=soniclayerdepth_value -12, xmax=soniclayerdepth_value + 3)
                criticaldepth_true = float("{0:.2f}".format(criticaldepth_true))
                plt.text(soniclayerdepth_value + 4, criticaldepth_true, "Critical Depth: " + str(criticaldepth_true) + 'm')

                # ~~~~~~~~~~~~~~

                # DEPTH EXCESS

                # First we have to find the last depth index with data
                max_depth = self.temperature_depths.data[0][ss.count() - 1] #- criticaldepth_true
                depthexcess = max_depth - criticaldepth_true
                depthexcess = float("{0:.2f}".format(depthexcess))
                plt.text( soniclayerdepth_value - 20, (criticaldepth_true + (depthexcess / 2)), "Depth Excess: " + str(depthexcess) + 'm')
                # ~~~~~~~~~~~~

            minpos = self.temperature_depths.data[0][minpos][0]
            maxpos = np.where(self.sspeed[0] == maxspeed)

            #plt.axvline(x=minspeed, ymin=0.5, ymax=1)
            #plt.axhline(y=minpos)
        
        if 'xscale' in self.query:
            ax.set_xlim(float(self.query.get('xscale')[0]), float(self.query.get('xscale')[1]))
        else:
            ax.set_xlim([
                np.amin(self.sspeed) - (maxspeed - minspeed) * 0.1,
                np.amax(self.sspeed) + (maxspeed - minspeed) * 0.1,
            ])

        if self.query.get('annotate'):
            # Sound Speed Minima
            minspeed = float("{0:.2f}".format(minspeed))
            plt.text(minspeed + 2, minpos, "Sound Channel Axis: " + str(minpos) + 'm')
            ax.scatter(minspeed, minpos, s=200, marker='_')
            # ~~~~~~~~~~~~~~~~~
        

        if 'xlabel' in self.query:
            ax.set_xlabel(gettext(self.query['xlabel']), fontsize=14)
        else:
            ax.set_xlabel(gettext("Sound Speed (m/s)"), fontsize=14)
        
        if 'ylabel' in self.query:
            ax.set_ylabel(gettext(self.query['ylabel']), fontsize=14)
        else:
            ax.set_ylabel(gettext("Depth (m)"), fontsize=14)
        
        ax.invert_yaxis()

        if ('yscale' in self.query):
            ax.set_ylim(float(self.query.get('yscale')[0]), float(self.query.get('yscale')[1]))

        ax.xaxis.set_ticks_position('top')
        ax.xaxis.set_label_position('top')
        x_format = tkr.FuncFormatter(lambda x, pos: "%d" % x)
        ax.xaxis.set_major_formatter(x_format)

        if not self.plotTitle:
            ax.set_title(gettext("Sound Speed Profile for (%s)\n%s") % (
                ", ".join(self.names), self.date_formatter(self.iso_timestamp)
            ), fontsize=15)
        else:
            ax.set_title(self.plotTitle, fontsize=15)

        ax.title.set_position([0.5, 1.10])
        plt.subplots_adjust(top=0.85)
        ax.xaxis.grid(True)

        self.plot_legend(fig, self.names)

        ylim = ax.get_ylim()
        ax2 = ax.twinx()
        ureg = pint.UnitRegistry()
        ax2.set_ylim((ylim * ureg.meters).to(ureg.feet).magnitude)
        ax2.set_ylabel(gettext("Depth (ft)"), fontsize=14)

        # This is a little strange where we want to skip calling the TSP.plot and go straigh
        # to Point.plot
        return super(TemperatureSalinityPlotter, self).plot(fig)

    def csv(self):
        header = [
            ["Dataset", self.dataset_name],
            ["Timestamp", self.iso_timestamp]
        ]

        columns = [
            "Latitude",
            "Longitude",
            "Depth (m)",
            "Pressure",
            "Salinity",
            "Temperature",
            "Sound Speed"
        ]

        data = []

        # For each point
        for idx, p in enumerate(self.points):
            for idx2, val in enumerate(self.temperature[idx]):
                if np.ma.is_masked(val):
                    break
                data.append([
                    "%0.4f" % p[0],
                    "%0.4f" % p[1],
                    "%0.1f" % self.temperature_depths[idx][idx2],
                    "%0.1f" % self.pressure[idx][idx2],
                    "%0.1f" % self.salinity[idx][idx2],
                    "%0.1f" % self.temperature[idx][idx2],
                    "%0.1f" % self.sspeed[idx][idx2]
                ])

        return super(TemperatureSalinityPlotter, self).csv(
            header, columns, data
        )
