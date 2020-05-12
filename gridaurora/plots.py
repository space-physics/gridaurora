import logging
from datetime import datetime
from pathlib import Path
import h5py
import xarray
from numpy.ma import masked_invalid  # for pcolormesh, which doesn't like NaN
from matplotlib.pyplot import figure, draw, close
from matplotlib.colors import LogNorm
from matplotlib.ticker import MultipleLocator
from matplotlib.dates import SecondLocator, DateFormatter, MinuteLocator
from typing import List
import numpy as np
import os
import gridaurora.ztanh as ga
import gridaurora.opticalmod as gao

if os.name == "nt":
    import pathvalidate
else:
    pathvalidate = None
# IEEE Transactions requires 600 dpi

dymaj = 100
dymin = 20


def writeplots(
    fg, plotprefix, tind=None, odir=None, fmt=".png", anno=None, dpi=None, facecolor=None, doclose=True,
):
    try:
        if fg is None or odir is None:
            return
        # %%
        draw()  # Must have this here or plot doesn't update in animation multiplot mode!
        # TIF was not faster and was 100 times the file size!
        # PGF is slow and big file,
        # RAW crashes
        # JPG no faster than PNG

        suff = nametime(tind)

        if anno:
            fg.text(0.15, 0.8, anno, fontsize="x-large")
        if pathvalidate is not None:
            cn = Path(odir).expanduser() / pathvalidate.sanitize_filename(plotprefix + suff + fmt)
        else:
            cn = Path(odir).expanduser() / (plotprefix + suff + fmt)

        print("write", cn)

        if facecolor is None:
            facecolor = fg.get_facecolor()

        fg.savefig(cn, bbox_inches="tight", dpi=dpi, facecolor=facecolor, edgecolor="none")

        if doclose:
            close(fg)

    except Exception as e:
        logging.error(f"{e}  when plotting {plotprefix}")


def nametime(tind):
    if isinstance(tind, int) and tind < 1e6:
        return "{:03d}".format(tind)
    elif isinstance(tind, datetime):
        return tind.isoformat()[:-3]  # -3 truncates to millisecond digits only (arbitrary)
    elif tind is not None:
        return str(tind)
    else:  # is None
        return ""


# %%


def plotflux(E, E0, arc, base=None, hi=None, low=None, mid=None, ttxt="Differential Number Flux"):
    FMAX = 1e6
    FMIN = 1e2

    lblstr = ["{:.0f}".format(e0) for e0 in E0]

    ax = figure().gca()
    if np.isscalar(E0) and mid is not None:
        ax.loglog(E, hi, "k:")
        ax.loglog(E, low, "k:")
        ax.loglog(E, mid, "k:")
        ax.loglog(E, base, color="k")
    ax.loglog(E, arc, linewidth=2)

    ax.grid(True, which="both")
    ax.set_xlabel("Electron Energy [eV]")  # ,fontsize=afs,labelpad=-2)
    ax.set_ylabel("Flux  [cm$^{-2}$s$^{-1}$eV$^{-1}$sr$^{-1}$]")  # ,fontsize=afs)
    ax.set_title(ttxt)
    # ax.tick_params(axis='both', which='both')
    ax.autoscale(True, tight=True)
    ax.set_ylim((1e2, FMAX))
    ax.legend(lblstr, loc="best")  # ,prop={'size':'large'})
    # ax.set_xlim((1e2,1e4))
    # sns.despine(ax=ax)

    if base is not None:
        ax = figure().gca()
        ax.loglog(E, base)
        ax.set_ylim((FMIN, FMAX))
        # ax.set_xlim((1e2,1e4))
        ax.set_title("arc Gaussian base function, E0=" + str(E0) + "[eV]" + "\n Wbc: width, Q0: height")
        ax.set_xlabel("Electron Energy [eV]")
        ax.set_ylabel("Flux  [cm$^{-2}$s$^{-1}$eV$^{-1}$sr$^{-1}$]")
        ax.legend(lblstr)

        ax = figure().gca()
        ax.loglog(E, low)
        ax.set_ylim((FMIN, FMAX))
        ax.set_title("arc low (E<E0).  Bl: height, bh: slope")
        ax.set_xlabel("Electron Energy [eV]")
        ax.set_ylabel("Flux  [cm$^{-2}$s$^{-1}$eV$^{-1}$sr$^{-1}$]")

        ax = figure().gca()
        ax.loglog(E, mid)
        ax.set_ylim((FMIN, FMAX))
        ax.set_title("arc mid.  Bm:height, bm: slope")
        ax.set_xlabel("Electron Energy [eV]")
        ax.set_ylabel("Flux  [cm$^{-2}$s$^{-1}$eV$^{-1}$sr$^{-1}$]")

        ax = figure().gca()
        ax.loglog(E, hi)
        ax.set_ylim((FMIN, FMAX))
        ax.set_title("arc hi (E>E0).  Bhf: height, bh: slope")
        ax.set_xlabel("Electron Energy [eV]")
        ax.set_ylabel("Flux  [cm$^{-2}$s$^{-1}$eV$^{-1}$sr$^{-1}$]")


# %%


def ploteigver(
    EKpcolor, zKM, eigenprofile, vlim=(None,) * 6, sim=None, tInd=None, makeplot=None, prefix=None, progms=None,
):
    try:
        fg = figure()
        ax = fg.gca()
        # pcolormesh canNOT handle nan at all
        pcm = ax.pcolormesh(
            EKpcolor,
            zKM,
            masked_invalid(eigenprofile),
            edgecolors="none",  # cmap=pcmcmap,
            norm=LogNorm(),
            vmin=vlim[4],
            vmax=vlim[5],
        )
        ax.set_xlabel("Energy [eV]")
        ax.set_ylabel(r"$B_\parallel$ [km]")
        ax.autoscale(True, tight=True)
        ax.set_xscale("log")
        ax.yaxis.set_major_locator(MultipleLocator(dymaj))
        ax.yaxis.set_minor_locator(MultipleLocator(dymin))
        # %% title
        if tInd is not None:
            mptitle = str(tInd)
        else:
            mptitle = ""
        mptitle += "$P_{{eig}}$"
        if sim:
            mptitle += ", filter: {}".format(sim.opticalfilter)
            mptitle += str(sim.reacreq)

        ax.set_title(mptitle)  # ,fontsize=tfs)
        # %% colorbar
        cbar = fg.colorbar(pcm, ax=ax)
        cbar.set_label("[photons cm$^{-3}$s$^{-1}$]", labelpad=0)  # ,fontsize=afs)
        # cbar.ax.tick_params(labelsize=afs)
        # cbar.ax.yaxis.get_offset_text().set_size(afs)
        # %% ticks,lim
        ax.tick_params(axis="both", which="both", direction="out")
        ax.set_ylim(vlim[2:4])
        # %%
        writeplots(fg, prefix, tInd, makeplot, progms)
    except Exception as e:
        logging.error("tind {}   {}".format(tInd, e))


def plotT(T, mmsl):

    ax1 = figure().gca()
    for c in ["filter", "window", "qe", "atm"]:
        ax1.plot(T.wavelength_nm, T[c], label=c)
    ax1.set_xlim(mmsl[:2])
    ax1.set_title(f"{T.filename}  Component transmittance")
    #
    ax2 = figure().gca()
    for s in ["sys", "sysNObg3"]:
        ax2.plot(T.wavelength_nm, T[s], label=s)

    ax2.set_title(f"{T.filename}  System Transmittance")

    for a in (ax1, ax2):
        niceTax(a)


def niceTax(a):
    a.set_xlabel("wavelength (nm)")
    a.set_ylabel("Transmittance (unitless)")
    #   a.set_yscale('log')
    a.legend(loc="best")
    #    a.set_ylim(1e-2,1)
    a.invert_xaxis()
    a.grid(True, which="both")


def comparefilters(Ts):
    fg = figure()
    axs = fg.subplots(len(Ts), 1, sharex=True, sharey=True)

    for T, ax in zip(Ts, axs):
        try:
            ax.plot(T.wavelength_nm, T["filter"], label=T.filename)
        except ValueError:  # just a plain filter
            assert T.ndim == 1
            ax.plot(T.wavelength_nm, T, label=T.filename)

        forbidden = [630.0, 555.7]
        permitted = [391.4, 427.8, 844.6, 777.4]
        for ln in forbidden:
            ax.axvline(ln, linestyle="--", color="darkred", alpha=0.8)
        for ln in permitted:
            ax.axvline(ln, linestyle="--", color="darkgreen", alpha=0.8)

        ax.set_title(f"{T.filename}")

    fg.suptitle("Transmittance")

    ax.set_ylim((0, 1))
    ax.set_xlim(T.wavelength_nm[[-1, 0]])
    ax.set_xlabel("wavelength [nm]")


def plotz(z: np.ndarray):
    dz = np.gradient(z, edge_order=2)  # numpy>=1.9.1
    dzmed = np.median(dz)

    ax = figure().gca()
    ax.plot(dz, z)
    ax.axvline(dzmed, color="r", linestyle="--", label="median")
    ax.set_xlabel("grid spacing [km]")
    ax.set_ylabel("altitude [km]")
    ax.set_title("$N_p=$" + str(z.shape[0]))
    ax.grid(True)
    ax.legend(loc="best")


if __name__ == "__main__":
    from matplotlib.pyplot import show
    from argparse import ArgumentParser

    p = ArgumentParser(description="create continuously step sized grid")
    p.add_argument("-n", "--np", help="number of points in grid", type=int, default=300)
    p.add_argument("--zmin", help="bottom of grid", type=float, default=90)
    p.add_argument("--gmin", help="minimum grid spacing", type=float, default=1.5)
    p.add_argument("--gmax", help="max grid spacing", type=float, default=10.575)
    a = p.parse_args()

    zgrid = ga.setupz(a.np, a.zmin, a.gmin, a.gmax)
    plotz(zgrid)
    print(zgrid[-1])

    show()

# %% HIST


def plotOptMod(verNObg3gray, VERgray):
    """ called from either readTranscar.py or hist-feasibility/plotsnew.py """
    if VERgray is None and verNObg3gray is None:
        return

    fg = figure()
    ax2 = fg.gca()  # summed (as camera would see)

    if VERgray is not None:
        z = VERgray.alt_km
        Ek = VERgray.energy_ev.values

        #        ax1.semilogx(VERgray, z, marker='',label='filt', color='b')
        props = {"boxstyle": "round", "facecolor": "wheat", "alpha": 0.5}
        fgs, axs = fg.subplots(6, 6, sharex=True, sharey="row")
        axs = axs.ravel()  # for convenient iteration
        fgs.subplots_adjust(hspace=0, wspace=0)
        fgs.suptitle("filtered VER/flux")
        fgs.text(0.04, 0.5, "Altitude [km]", va="center", rotation="vertical")
        fgs.text(0.5, 0.04, "Beam energy [eV]", ha="center")
        for i, e in enumerate(Ek):
            axs[i].semilogx(VERgray.loc[:, e], z)
            axs[i].set_xlim((1e-3, 1e4))

            # place a text box in upper left in axes coords
            axs[i].text(
                0.95, 0.95, "{:0.0f}".format(e) + "eV", transform=axs[i].transAxes, fontsize=12, va="top", ha="right", bbox=props,
            )
        for i in range(33, 36):
            axs[i].axis("off")

        ax2.semilogx(VERgray.sum(axis=1), z, label="filt", color="b")

        # specific to energies
        ax = figure().gca()
        for e in Ek:
            ax.semilogx(VERgray.loc[:, e], z, marker="", label="{:.0f} eV".format(e))
        ax.set_title("filtered VER/flux")
        ax.set_xlabel("VER/flux")
        ax.set_ylabel("altitude [km]")
        ax.legend(loc="best", fontsize=8)
        ax.set_xlim((1e-5, 1e5))
        ax.grid(True)

    if verNObg3gray is not None:
        ax1 = figure().gca()  # overview
        z = verNObg3gray.alt_km
        Ek = verNObg3gray.energy_ev.values

        ax1.semilogx(verNObg3gray, z, marker="", label="unfilt", color="r")
        ax2.semilogx(verNObg3gray.sum(axis=1), z, label="unfilt", color="r")

        ax = figure().gca()
        for e in Ek:
            ax.semilogx(verNObg3gray.loc[:, e], z, marker="", label="{:.0f} eV".format(e))
        ax.set_title("UNfiltered VER/flux")
        ax.set_xlabel("VER/flux")
        ax.set_ylabel("altitude [km]")
        ax.legend(loc="best", fontsize=8)
        ax.set_xlim((1e-5, 1e5))
        ax.grid(True)

        ax1.set_title("VER/flux, one profile per beam")
        ax1.set_xlabel("VER/flux")
        ax1.set_ylabel("altitude [km]")
        ax1.grid(True)

    ax2.set_xlabel("VER/flux")
    ax2.set_ylabel("altitude [km]")
    ax2.set_title("VER/flux summed over all energy beams \n (as the camera would see)")
    ax2.legend(loc="best")
    ax2.grid(True)


def comparejgr2013(altkm, zenang, bg3fn, windfn, qefn):

    R = Path(__file__).parent

    with h5py.File(R / "precompute/trans_jgr2013a.h5", "r") as f:
        reqLambda = f["/lambda"][:]
        Tjgr2013 = f["/T"][:]

    optT = gao.getSystemT(reqLambda, bg3fn, windfn, qefn, altkm, zenang)

    ax = figure().gca()
    ax.semilogy(reqLambda, optT["sys"], "b", label="HST")
    ax.semilogy(reqLambda, Tjgr2013, "r", label="JGR2013")
    ax.set_xlabel("wavelength [nm]")
    ax.set_ylabel("T")
    ax.set_title("Comparision of Transmission models: HST vs. JGR2013")
    ax.grid(True)
    ax.legend(loc="best")
    ax.set_title("System Transmission + Atmospheric Absorption")
    ax.set_ylim(1e-10, 1)


def plotAllTrans(optT, log):
    mutwl = optT.wavelength_nm

    fg = figure(figsize=(7, 5))
    ax = fg.gca()
    ax.plot(mutwl, optT["sys"], label="optics")
    ax.plot(mutwl, optT["atm"], label="atmosphere")
    ax.plot(mutwl, optT["sys"] * optT["atm"], label="total", linewidth=2)
    if log:
        ax.set_yscale("log")
        ax.set_ylim(bottom=1e-5)
    ax.set_xlabel("wavelength [nm]")
    ax.set_ylabel("Transmission [dimensionless]")
    ax.set_title("System Transmission")
    ax.grid(True, "both")
    ax.invert_xaxis()
    ax.xaxis.set_major_locator(MultipleLocator(100))
    ax.legend(loc="center", bbox_to_anchor=(0.3, 0.15))

    return fg


def plotPeigen(Peigen):
    # Peigen: Nalt x Nenergy
    if not isinstance(Peigen, xarray.DataArray):
        return

    fg = figure()
    ax = fg.gca()
    pcm = ax.pcolormesh(Peigen.energy_ev, Peigen.alt_km, Peigen.values)
    ax.autoscale(True, tight=True)
    ax.set_xscale("log")
    ax.set_xlabel("beam energy [eV]")
    ax.set_ylabel("altitude [km]")
    ax.set_title("Volume Emission Rate per unit diff num flux")
    fg.colorbar(pcm)


def showIncrVER(
    tTC: np.ndarray,
    tReqInd: int,
    tctime: np.ndarray,
    ver: xarray.DataArray,
    tver: xarray.DataArray,
    titxt: str,
    makePlots: List[str],
):
    saveplot = False
    z = ver.alt_km
    lamb = ver.wavelength

    # if 'spectra1d' in makePlots:
    # b = np.trapz(ver, z, axis=1)  # integrate along z, looking up magnetic zenith
    # plotspectra(b, lamb)

    if "eigtime" in makePlots:
        fg = figure(figsize=(11, 8), dpi=100, tight_layout=True)
        ax = fg.gca()

        pcm = ax.pcolormesh(
            tTC, z, tver.sum(axis=0), edgecolors="none", cmap=None, norm=None, vmin=0, vmax=1e3,  # sum over wavelength
        )

        ax.axvline(tTC[tReqInd], color="white", linestyle="--", label="Req. Time")
        ax.axvline(tctime["tstartPrecip"], color="red", linestyle="--", label="Precip. Start")
        ax.axvline(tctime["tendPrecip"], color="red", linestyle="--", label="Precip. End")

        titlemean = titxt + (
            r"\n VER/flux: $\lambda \in$"
            + str(lamb)
            + " [nm]"
            + "\n geodetic lat:"
            + str(tctime["latgeo_ini"])
            + " lon:"
            + str(tctime["longeo_ini"])
            + " date: "
            + tctime["dayofsim"].strftime("%Y-%m-%d")
        )
        # make room for long title
        fg.subplots_adjust(top=0.8)

        ax.set_title(titlemean, fontsize=9)

        ax.yaxis.set_major_locator(MultipleLocator(100))
        ax.yaxis.set_minor_locator(MultipleLocator(20))

        # ax.xaxis.set_major_locator(MinuteLocator(interval=10))
        ax.xaxis.set_major_locator(MinuteLocator(interval=1))
        ax.xaxis.set_minor_locator(SecondLocator(interval=10))
        ax.xaxis.set_major_formatter(DateFormatter("%H:%M:%S"))

        ax.tick_params(axis="both", which="both", direction="out", labelsize=12)

        ax.autoscale(True, tight=True)
        cbar = fg.colorbar(pcm)
        cbar.set_label("VER/flux", labelpad=0)
        ax.set_xlabel("Time [UTC]")
        ax.set_ylabel("altitude [km]")
        if saveplot:
            sfn = "".join(e for e in titxt if e.isalnum() or e == ".")  # remove special characters
            fg.savefig("out/VER" + sfn + ".png", dpi=150, bbox_inches="tight")
            close(fg)

    if "eigtime1d" in makePlots:
        fg = figure(figsize=(11, 8), dpi=100)
        ax = fg.gca()
        # fg.subplots_adjust(top=0.85)
        thistitle = titxt + ": {:d} emission lines\n VER/flux:  geodetic lat: {} lon: {}  {}".format(
            ver.shape[0], tctime["latgeo_ini"], tctime["longeo_ini"], tTC[tReqInd]
        )
        ax.set_title(thistitle, fontsize=12)
        ax.set_xlabel("VER/flux")
        ax.set_ylabel("altitude [km]")

        for ifg, clamb in enumerate(lamb):
            ax.semilogx(ver.iloc[ifg, :], z, label=str(clamb))

        ax.yaxis.set_major_locator(MultipleLocator(100))
        ax.yaxis.set_minor_locator(MultipleLocator(20))
        ax.grid(True)
        if ver.shape[0] < 20:
            ax.legend(
                loc="upper center", bbox_to_anchor=(1.05, 0.95), ncol=1, fancybox=True, shadow=True, fontsize=9,
            )

        ax.tick_params(axis="both", which="both", direction="in", labelsize=12)

        ax.set_xlim(1e-9, 1e3)
        ax.set_ylim((z[0], z[-1]))

        if saveplot:
            sfn = "".join(e for e in titxt if e.isalnum())  # remove special characters
            fg.savefig("out/VER" + sfn + ".png", dpi=150, bbox_inches="tight")
            close(fg)


def plotspectra(br, optT: xarray.DataArray, E: float, lambminmax: tuple):

    spectraAminmax = (1e-1, 8e5)  # for plotting
    spectrallines = (
        391.44,
        427.81,
        557.7,
        630.0,
        777.4,
        844.6,
    )  # 297.2, 636.4,762.0, #for plotting

    lamb = optT.wavelength_nm

    def _plotspectrasub(ax, bf, txt):
        ax.set_yscale("log")
        ax.set_title("Auroral spectrum, " + txt + f",integrated along flux tube: $E_0$ = {E:.0f} eV")
        ax.set_ylabel("optical intensity")
        ax.set_xlim(lambminmax)
        ax.set_ylim(spectraAminmax)
        ax.xaxis.set_major_locator(MultipleLocator(100))
        # ax.invert_xaxis()

        for ln in spectrallines:
            ax.text(
                ln, bf[ln] * 1.7, "{:.1f}".format(ln), ha="center", va="bottom", fontsize="medium", rotation=60,
            )

    # %%
    fg = figure()
    ax1, ax2 = fg.subplots(2, 1, sharex=True, figsize=(10, 8))

    bf = br * optT["sysNObg3"]
    ax1.stem(lamb, bf)
    _plotspectrasub(ax1, bf, "no filter")

    bf = br * optT["sys"]
    ax2.stem(lamb, bf)
    _plotspectrasub(ax2, bf, "BG3 filter")
    ax2.set_xlabel("wavelength [nm]")

    return fg
