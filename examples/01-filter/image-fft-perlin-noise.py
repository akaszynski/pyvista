"""
.. _image_fft_perlin_example:

Fast Fourier Transform with Perlin Noise
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This example shows how to apply a Fast Fourier Transform (FFT) to a
:class:`pyvista.UniformGrid` using :func:`pyvista.UniformGridFilters.fft`
filter.

Here, we demonstrate FFT usage by first generating Perlin noise using
:func:`pyvista.sample_function() <pyvista.core.imaging.sample_function>` to
sample :func:`pyvista.perlin_noise <pyvista.core.common_data.perlin_noise>`,
and then performing FFT of the sampled noise to show the frequency content of
that noise.

"""

import numpy as np

import pyvista as pv

###############################################################################
# Start by generating some `Perlin Noise
# <https://en.wikipedia.org/wiki/Perlin_noise>`_ as in
# :ref:`perlin_noise_2d_example` example.
#
# Note that we are generating it in a flat plane and using a frequency of 10 in
# the x direction and 5 in the y direction. Units of the frequency is
# ``1/pixel``.
#
# Also note that the dimensions of the image are a power of 2. This is because
# the FFT is most efficient for images dimensioned in a power of 2.

freq = [10, 5, 0]
noise = pv.perlin_noise(1, freq, (0, 0, 0))
xdim, ydim = (512, 512)
sampled = pv.sample_function(noise, bounds=(0, 10, 0, 10, 0, 10), dim=(xdim, ydim, 1))

# plot the sampled noise
sampled.plot(cpos='xy', show_scalar_bar=False, text='Perlin Noise')

###############################################################################
# Next, perform a FFT of the noise and plot the frequency content.
# For the sake of simplicity, we will only plot the content in the first
# quadrant.
#
# Note the usage of :func:`numpy.fft.fftfreq` to get the frequencies.
#
sampled_fft = sampled.fft()
freq = np.fft.fftfreq(sampled.dimensions[0], sampled.spacing[0])

# only show the first quadrant
subset = sampled_fft.extract_subset((0, xdim // 4, 0, ydim // 4, 0, 0))

# shift the position of the uniform grid to match the frequency
subset.origin = (0, 0, 0)
spacing = np.diff(freq[:2])[0]
subset.spacing = (spacing, spacing, spacing)


###############################################################################
# Now, plot the noise in the frequency domain. Note how there is more high
# frequency content in the x direction and this matches the frequencies given
# to :func:`pyvista.perlin_noise <pyvista.core.common_data.perlin_noise>`.

pl = pv.Plotter()
pl.add_mesh(subset, cmap='gray', show_scalar_bar=False)
pl.camera_position = 'xy'
pl.show_bounds(xlabel='X Frequency', ylabel='Y Frequency')
pl.add_text('Frequency Domain of the Perlin Noise')
pl.show()

###############################################################################
# Low Pass Filter
# ~~~~~~~~~~~~~~~
# Let's perform a low pass filter on the frequency content and then convert it
# back into the space (pixel) domain by immediately applying a reverse FFT.
#
# When converting back, keep only the real content. The imaginary content has no
# physical meaning in the physical domain.
#
# As expected, we only see low frequency noise.

low_pass = sampled_fft.low_pass(1.0, 1.0, 1.0).rfft()
low_pass['scalars'] = low_pass.active_scalars.real
low_pass.plot(cpos='xy', show_scalar_bar=False, text='Low Pass of the Perlin Noise')
# low_pass.plot(scalars=low_pass.active_scalars.real, cpos='xy', show_scalar_bar=True, text='Low Pass of the Perlin Noise')


###############################################################################
# High Pass Filter
# ~~~~~~~~~~~~~~~~
# This time, let's perform a high pass filter on the frequency content and then
# convert it back into the space (pixel) domain by immediately applying a
# reverse FFT.
#
# When converting back, keep only the real content. The imaginary content has no
# physical meaning in the pixel domain.
#
# As expected, we only see the high frequency noise content as the low
# frequency noise has been attenuated.

high_pass = sampled_fft.high_pass(1.0, 1.0, 1.0).rfft()
high_pass['scalars'] = high_pass.active_scalars.real
high_pass.plot(cpos='xy', show_scalar_bar=False, text='High Pass of the Perlin Noise')

###############################################################################
# Show that the low and high passes of the original noise sum to the original.

grid = pv.UniformGrid(dims=(xdim, ydim, 1))
grid['scalars'] = high_pass['scalars'] + low_pass['scalars']

pl = pv.Plotter(shape=(1, 2))
pl.add_mesh(sampled, show_scalar_bar=False)
pl.add_text('Original Dataset')
pl.camera_position = 'xy'
pl.subplot(0, 1)
pl.add_mesh(grid, show_scalar_bar=False)
pl.add_text('Summed Low and High Passes')
pl.camera_position = 'xy'
pl.show()
