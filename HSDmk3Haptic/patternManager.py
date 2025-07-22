import threading
import time
import numpy as np
import math
import matplotlib.pyplot as plt

class PatternManager:
    def __init__(self):
        # Gestion des patterns
        self.patternRunning = False
        self.patternCurrent = None
        self.patternPosition = []
        self.patternSpeed= 1.0
        self.patternDuration = 2.0
        self.nPattern = 200
        self.numRoundTrips = 1  # Nombre d'aller-retours pour le pattern horizontal

        # Intensités des ports
        self.portIntensities = {port: 1.0 for port in range(6)}  
        self.logIntensity = np.ones((6, self.nPattern))  

    def configurePatternFromPreset(self, preset):
        self.patternCurrent = preset.pattern
        self.patternSpeed= preset.speed
        self.patternDuration = preset.duration
        self.numRoundTrips = preset.numRoundTrip if hasattr(preset, 'numRoundTrip') else 1
        print(self.numRoundTrips)
        self.adjustPatternSpeed(self.patternSpeed)
        self.startPattern()

    def adjustPatternSpeed(self, patternSpeed):
        self.patternDuration /= patternSpeed
        self.nPattern = int(self.nPattern * patternSpeed)
        self.logIntensity = np.ones((6, self.nPattern)) 


    def startPattern(self):
        if self.patternCurrent is None:
            return

        patterns = {
            "Circulaire": self.circularPattern,
            "DroiteGauche": self.RLPattern,
            "Diagonal": self.diagonalPattern,
            "Horizontal": self.horizonPattern,
            "Vertical": self.verticalPattern
        }

        if self.patternCurrent not in patterns:
            raise ValueError(f"Pattern '{self.patternCurrent}' non reconnu")

        self.patternRunning = True
        patterns[self.patternCurrent]()
        self.patternRunning = False

    def circularPattern(self):
        center_x, center_y = 0.5, 0.5
        radius = 0.3
        angle = 0

        for i in range(self.nPattern):
            if not self.patternRunning:
                break
            angle += 2 * math.pi / self.nPattern
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self.updateIntensitiesFromPosition(x, y)
            self.patternPosition.append((x, y))
            self.logIntensities(i)

    def RLPattern(self):
        min_x, max_x = 0.1, 0.9
        y = 0.5

        points_per_trip = self.nPattern // self.numRoundTrips
        total_steps = points_per_trip * self.numRoundTrips
        self.logIntensity = np.ones((6, total_steps))  # Redimensionner correctement le log

        for trip in range(self.numRoundTrips):
            x_vals = np.linspace(max_x, min_x, points_per_trip)
            for i in range(points_per_trip):
                if not self.patternRunning:
                    break
                x = x_vals[i]
                self.updateIntensitiesFromPosition(x, y)
                self.patternPosition.append((x, y))
                step = trip * points_per_trip + i
                self.logIntensities(step)


    def diagonalPattern(self):
        points = [(0.1, 0.1), (0.9, 0.9), (0.1, 0.9), (0.9, 0.1)]
        current_point = 0

        for i in range(self.nPattern):
            if not self.patternRunning:
                break
            start_point = points[current_point]
            next_point = points[(current_point + 1) % len(points)]

            progress = i / self.nPattern
            x = start_point[0] + (next_point[0] - start_point[0]) * progress
            y = start_point[1] + (next_point[1] - start_point[1]) * progress

            self.updateIntensitiesFromPosition(x, y)
            self.patternPosition.append((x, y))
            self.logIntensities(i)

            if i == self.nPattern - 1:
                current_point = (current_point + 1) % len(points)

    def horizonPattern(self):
        min_x, max_x = 0.1, 0.9
        y = 0.5
        self.numRoundTrips  = 12  # Nombre d'aller-retours

        # Calcul du nombre total de points pour chaque aller-retour
        points_per_trip = self.nPattern // (2 * self.numRoundTrips )

        for trip in range(self.numRoundTrips ):
            # Aller
            for i in range(points_per_trip):
                if not self.patternRunning:
                    break
                x = np.linspace(min_x, max_x, points_per_trip)[i]
                self.updateIntensitiesFromPosition(x, y)
                self.patternPosition.append((x, y))
                self.logIntensities(trip * 2 * points_per_trip + i)

            # Retour
            for i in range(points_per_trip):
                if not self.patternRunning:
                    break
                x = np.linspace(max_x, min_x, points_per_trip)[i]
                self.updateIntensitiesFromPosition(x, y)
                self.patternPosition.append((x, y))
                self.logIntensities(trip * 2 * points_per_trip + points_per_trip + i)

    def verticalPattern(self):
        min_y, max_y = 0.1, 0.9
        x = 0.5

        for i in range(self.nPattern//2):
            if not self.patternRunning:
                break
            y = np.linspace(min_y, max_y, self.nPattern//2)[i]
            self.updateIntensitiesFromPosition(x, y)
            self.patternPosition.append((x, y))
            self.logIntensities(i)

        for i in range(self.nPattern//2):
            if not self.patternRunning:
                break
            y = np.linspace(max_y, min_y, self.nPattern//2)[i]
            self.updateIntensitiesFromPosition(x, y)
            self.patternPosition.append((x, y))
            self.logIntensities(i+self.nPattern//2) 

    def updateIntensitiesFromPosition(self, x, y):
        # Points des actioneurs
        xc1, yc1 = 0.1, 0.1
        xc2, yc2 = 0.9, 0.1
        xc3, yc3 = 0.1, 0.9
        xc4, yc4 = 0.9, 0.9
        xc5, yc5 = 0.5, 0.1
        xc6, yc6 = 0.5, 0.9

        gamma = (x - xc1) / (xc2 - xc1)
        beta = (y - yc1) / (yc4 - yc1)

        # Interpoaltion des intensités
        Iv = 1  # Intensité Actionneur Fantôme
        I1, I2, I3, I4, I5, I6 = self.get_Intensities(Iv, x, gamma, beta)

        # Valeur entre 0 et 1
        I1 = max(0, min(I1, 1))
        I2 = max(0, min(I2, 1))
        I3 = max(0, min(I3, 1))
        I4 = max(0, min(I4, 1))
        I5 = max(0, min(I5, 1))
        I6 = max(0, min(I6, 1))

        self.portIntensities[0] = I1
        self.portIntensities[1] = I2
        self.portIntensities[2] = I3
        self.portIntensities[3] = I4
        self.portIntensities[4] = I5
        self.portIntensities[5] = I6

    # Calcul Interpolation des intensités
    def get_Intensities(self, Iv, s_center_x, gamma, beta):
        xc1, xc5, xc2 = 0.1, 0.5, 0.9  
        if (gamma < 0.5): 
            alpha = (s_center_x - xc1) / (xc5 - xc1)
            I1 = (1 - alpha) * (1 - beta) * Iv
            I2 = 0
            I3 = (1 - alpha) * beta * Iv
            I4 = 0
            I5 = alpha * (1 - beta) * Iv
            I6 = alpha * beta * Iv
        elif (gamma > 0.5):
            alpha = (s_center_x - xc5) / (xc2 - xc5)
            I1 = 0
            I2 = alpha * (1 - beta) * Iv
            I3 = 0
            I4 = alpha * beta * Iv
            I5 = (1 - alpha) * (1 - beta) * Iv
            I6 = (1 - alpha) * beta * Iv
        elif (gamma == 0.5):
            I1 = 0
            I2 = 0
            I3 = 0
            I4 = 0
            I5 = (1 - beta) * Iv
            I6 = beta * Iv
        return I1, I2, I3, I4, I5, I6

    def logIntensities(self, step):
        for port in range(6):
            self.logIntensity[port, step] = self.portIntensities[port]

    def visualizePattern(self):
        plt.ion()
        fig, ax = plt.subplots()
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        scatter = ax.scatter([], [])
        text = ax.text(0.05, 0.95, '', transform=ax.transAxes, verticalalignment='top')

        centers = [(0.1, 0.1), (0.9, 0.1), (0.1, 0.9), (0.9, 0.9), (0.5, 0.1), (0.5, 0.9)]
        for i, (xc, yc) in enumerate(centers):
            ax.text(xc, yc, f'Port {i+1}', fontsize=12, ha='center')

        while self.patternRunning:
            if self.patternPosition:
                x, y = self.patternPosition[-1]  
                scatter.set_offsets(np.c_[[x], [y]])
                intensities = '\n'.join([f'Port {port + 1}: {intensity:.2f}' for port, intensity in self.portIntensities.items()])
                text.set_text(intensities)
                plt.draw()
                plt.pause(0.01)
            # time.sleep(self.patternDelay)

        plt.ioff()
        plt.show()

# # Example usage
# if __name__ == "__main__":
#     from presetTouch import PresetsTouch

#     presets = PresetsTouch()
#     pattern_manager = PatternManager()

#     # Configure pattern from preset
#     pattern_manager.configurePatternFromPreset(presets.Carresse2)

#     # Print the intensity log
#     print(pattern_manager.logIntensity)
#     plt.figure()
#     plt.imshow(pattern_manager.logIntensity, aspect='auto', cmap='viridis')
#     plt.xlabel("Pattern step")
#     plt.ylabel("Port")
#     plt.title("Intensity log")
#     plt.colorbar()
#     plt.show()