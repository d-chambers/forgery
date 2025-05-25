"""
Utilities for fervo interview code.
"""

from dataclasses import dataclass

import pyvista as pv
import shapely

from .data import csv_data, get_well_data, shp_data


@dataclass
class ForgeVistaScene:
    """A class for building the Forge model."""

    surface_df = csv_data["surface"]
    granitoid_df = csv_data["granitoid"]
    fault_dfs = csv_data["faults"]
    event_df = csv_data["events"]
    extents = shp_data["extents"]
    wells_dfs = get_well_data()
    mag_min = -0.5

    def get_plotter(self):
        pl = pv.Plotter()
        pl.enable_terrain_style()
        return pl

    def _get_surface(self, xyz, constrain_to_extents=False):
        if constrain_to_extents:
            poly = self.extents.iloc[0]["geometry"]
            in_poly = shapely.contains_xy(poly, xyz[:, 0], xyz[:, 1])
            xyz = xyz[in_poly]
        cloud = pv.PolyData(xyz)
        surface = cloud.delaunay_2d()
        return surface

    def get_surface(self):
        """Create a surface from the surface."""
        xyz = self.surface_df[["x", "y", "z"]].values
        return self._get_surface(xyz, constrain_to_extents=True)

    def get_faults_surfaces(self):
        """Add the fault surfaces to the plot."""
        out = {}
        for name, fault in self.fault_dfs.items():
            out[name] = self._get_surface(fault[["x", "y", "z"]].values)
        return out

    def get_granitoid(self):
        xyz = self.granitoid_df[["x", "y", "z"]].values
        surf = self._get_surface(xyz, constrain_to_extents=True)
        return surf

    def add_wells_to_plotter(self, plotter):
        """Add the wells as lines."""
        for name, df in self.wells_dfs.items():
            lines = df[["east", "north", "elevation"]].values
            plotter.add_lines(lines, connected=True, color="grey")

    def _get_radius(self, mags, max_rad, min_rad):
        """Get the event radii."""
        mag_min, mag_max = mags.min(), mags.max()
        dist_mag = mag_max - mag_min
        mag_scale = (mags - mag_min) / dist_mag
        rad_dist = max_rad - min_rad
        return min_rad + mag_scale * rad_dist

    def add_event_gyphs(self, pl, max_radius=100, min_radius=20):
        """Plot the event glyphs."""
        edf = self.event_df[self.event_df["magnitude"] > self.mag_min]
        # Need to get elevation for events (only depth given)
        # Use the highest well point.
        max_el = 0
        for name, df in self.wells_dfs.items():
            elev = df["elevation"].values.max()
            max_el = max([max_el, elev])
        df = edf.assign(elevation=max_el - edf["depth"])

        # Get radii of events.
        mags = edf["magnitude"].values
        radii = self._get_radius(mags, max_radius, min_radius)

        poly = pv.PolyData(df[["east", "north", "elevation"]].values)
        poly["magnitude"] = mags
        poly["radius"] = radii

        smooth_sphere = pv.Sphere(radius=1.0, theta_resolution=16, phi_resolution=16)

        glyphs = poly.glyph(geom=smooth_sphere, factor=1.0, scale="radius")
        glyphs.active_scalars_name = "magnitude"

        pl.add_mesh(
            glyphs,
            scalars="magnitude",
            cmap="viridis",
            show_scalar_bar=True,
            # scalar_bar_args=scalar_bar_args,
            clim=[mags.min(), mags.max()],
            smooth_shading=True,
        )

        pl.show_axes()

        return glyphs

    def __call__(self):
        pl = self.get_plotter()
        surface = self.get_surface()
        granitoid = self.get_granitoid()
        pl.add_mesh(surface, opacity=0.25)
        pl.add_mesh(granitoid, color="red", opacity=0.15)
        self.add_wells_to_plotter(pl)
        glyphs = self.add_event_gyphs(pl)
        pl.add_mesh(glyphs)
        # pl.show_bounds(
        #     grid='front', location='outer', all_edges=True,
        #     xtitle='', ytitle='', ztitle='',  # Remove axis labels
        #     xlabel='', ylabel='', zlabel=''  # Remove tick labels (optional redundancy)
        # )
        # Access the axes actor and modify labels
        axes = pl.renderer.axes_actor
        axes.SetXAxisLabelText("East")
        axes.SetYAxisLabelText("North")
        axes.SetZAxisLabelText("Z")
        return pl
