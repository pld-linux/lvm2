# TODO
# - lvmlockd-idm (BR: pkgconfig(libseagate_ilm) >= 0.1.0 - https://github.com/Seagate/propeller ?)
# - vgscan --ignorelocking failure creates /var/lock/lvm (even if /var is not yet mounted)
# - internal vs shared for snapshots,mirrors,thin,cache ?
#   note: dmeventd requires mirrors=internal)
#
# Conditional build:
# - initrd stuff
%bcond_with	initrd		# build initrd version
# - functionality
%bcond_without	cluster		# disable all cluster support (cmirrord, dlm support in lvmlockd)
%bcond_without	lvmdbusd	# lvmdbusd
%bcond_without	lvmpolld	# lvmpolld (and lvmlockd)
%bcond_without	lvmlockd	# lvmlockd
%bcond_without	sanlock		# sanlock support in lvmlockd
# - additional features
%bcond_without	selinux		# SELinux support

# lvmlockd requires lvmpolld
%if %{without lvmpolld}
%undefine	with_lvmlockd
%endif

%if %{without cluster} && %{without sanlock}
%undefine	with_lvmlockd
%endif

Summary:	The new version of Logical Volume Manager for Linux
Summary(pl.UTF-8):	Nowa wersja Logical Volume Managera dla Linuksa
Name:		lvm2
Version:	2.03.29
Release:	1
License:	GPL v2 and LGPL v2.1
Group:		Applications/System
Source0:	ftp://sourceware.org/pub/lvm2/LVM2.%{version}.tgz
# Source0-md5:	034e43bc84969536411742252df78dbf
Patch0:		device-mapper-dmsetup-export.patch
Patch1:		%{name}-pld_init.patch
Patch2:		device-mapper-dmsetup-deps-export.patch
Patch3:		%{name}-thin.patch
URL:		https://www.sourceware.org/lvm2/
BuildRequires:	autoconf >= 2.69
BuildRequires:	autoconf-archive
BuildRequires:	automake
# for /run detection
BuildRequires:	filesystem >= 3.0-43
BuildRequires:	libaio-devel
BuildRequires:	libblkid-devel >= 2.24
%{?with_selinux:BuildRequires:	libselinux-devel >= 1.10}
%{?with_selinux:BuildRequires:	libsepol-devel}
BuildRequires:	ncurses-devel
BuildRequires:	pkgconfig
%if %{with lvmdbusd}
BuildRequires:	python3-dbus
BuildRequires:	python3-devel >= 1:3.2
BuildRequires:	python3-pyudev
%endif
BuildRequires:	readline-devel
BuildRequires:	rpmbuild(macros) >= 1.647
%{?with_sanlock:BuildRequires:	sanlock-devel >= 3.7}
BuildRequires:	systemd-devel >= 1:234
BuildRequires:	udev-devel >= 1:176
%if %{with initrd}
%{?with_selinux:BuildRequires:	libselinux-static}
%{?with_selinux:BuildRequires:	libsepol-static}
BuildRequires:	glibc-static
BuildRequires:	libaio-static
%{?with_selinux:BuildRequires:	pcre-static}
%else
Obsoletes:	lvm2-initrd < %{version}-%{release}
%endif
%if %{with cluster}
# for cmirrord
BuildRequires:	corosync-devel
# for dlm support in lvmlockd
BuildRequires:	dlm-devel >= 3.99.5
%endif
Requires(post,preun,postun):	systemd-units >= 1:234
Requires(post,postun):	/sbin/chkconfig
Requires:	device-mapper >= %{version}-%{release}
%{?with_selinux:Requires:	libselinux >= 1.10}
Requires:	systemd-units >= 1:234
# doesn't work with 2.4 kernels
Requires:	uname(release) >= 2.6
%{?with_lvmlockd:Suggests:	%{name}-lockd = %{version}-%{release}}
Suggests:	thin-provisioning-tools >= 0.7.0
Obsoletes:	lvm < 2
Obsoletes:	lvm2-clvmd < 2.03
Obsoletes:	lvm2-systemd < 2.02.94
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sbindir	/sbin
%define		_usrsbindir	/usr/sbin

# changing CFLAGS in the middle confuses confcache
%undefine	configure_cache

# causes: undefined reference to `__stack_chk_fail_local'
%define		filterout_c	-fstack-protector

%define		skip_post_check_so	'.*libdevmapper-event-lvm2.so.*' 'liblvm2cmd.so.*'

%description
This package includes a number of utilities for creating, checking,
and repairing logical volumes.

%description -l pl.UTF-8
Pakiet ten zawiera narzędzia do tworzenia, sprawdzania i naprawiania
logicznych wolumenów dyskowych (LVM2).

%package initrd
Summary:	The new version of Logical Volume Manager for Linux - initrd version
Summary(pl.UTF-8):	Nowa wersja Logical Volume Managera dla Linuksa - wersja dla initrd
Group:		Base
Conflicts:	geninitrd < 10000.18

%description initrd
This package includes a number of utilities for creating, checking,
and repairing logical volumes - staticaly linked for initrd.

%description initrd -l pl.UTF-8
Pakiet ten zawiera narzędzia do tworzenia, sprawdzania i naprawiania
logicznych wolumenów dyskowych (LVM2) - statycznie skonsolidowane na
potrzeby initrd.

%package cmirrord
Summary:	Cluster mirror log daemon
Summary(pl.UTF-8):	Demon śledzący log lustrzany w klastrze
Group:		Applications/System
Requires:	%{name} = %{version}-%{release}

%description cmirrord
cmirrord is the daemon that tracks mirror log information in a
cluster. It is specific to device-mapper based mirrors (and by
extension, LVM cluster mirrors). Cluster mirrors are not possible
without this daemon running.

This daemon relies on the cluster infrastructure provided by the
Cluster MANager (CMAN), which must be set up and running in order for
cmirrord to function.

%description cmirrord -l pl.UTF-8
cmirrord to demon śledzący informacje logu lustrzanego w klastrze.
Jest specyficzny dla klastrów lustrzanych opartych na device-mapperze
(oraz, poprzez rozszerzenie, klastrów lustrzanych LVM). W klastrach
lustrzanych ten demon jest niezbędny.

Ten demon polega na infrastrukturze klastra dostarczanej przez CMAN
(Cluster MANager), który musi być skonfigurowany i działający, aby
działał cmirrord.

%package dbusd
Summary:	LVM2 D-Bus daemon
Summary(pl.UTF-8):	Demon LVM2 D-Bus
Group:		Daemons
Requires(post,preun,postun):	systemd-units >= 1:234
Requires:	%{name} = %{version}-%{release}
Requires:	python3-dbus
Requires:	python3-pygobject3 >= 3
Requires:	python3-pyudev

%description dbusd
Daemon for access to LVM2 functionality through a D-Bus interface.

%description dbusd -l pl.UTF-8
Demon umożliwiający dostęp do funkcjonalności LVM2 poprzez interfejs
D-Bus.

%package lockd
Summary:	LVM2 locking daemon
Summary(pl.UTF-8):	Demon blokad LVM2
Group:		Daemons
Requires(post,preun,postun):	systemd-units >= 1:234
Requires:	%{name} = %{version}-%{release}
%{?with_cluster:Requires:	dlm-libs >= 3.99.5}
%{?with_sanlock:Requires:	sanlock-libs >= 3.7}

%description lockd
LVM commands use lvmlockd to coordinate access to shared storage.

%description lockd -l pl.UTF-8
Polecenia LVM wykorzystują lvmlockd do koordynowania dostępu do
współdzielonej pamięci masowej.

%package resource-agents
Summary:	OCF Resource Agents for LVM2 processes
Summary(pl.UTF-8):	Agenci OCF do monitorowania procesów LVM2
Group:		Applications/System
Requires:	%{name} = %{version}-%{release}
Requires:	resource-agents

%description resource-agents
OCF Resource Agents for LVM2 processes.

%description resource-agents -l pl.UTF-8
Agenci OCF do monitorowania procesów LVM2.

%package -n device-mapper
Summary:	Userspace support for the device-mapper
Summary(pl.UTF-8):	Wsparcie dla mapowania urządzeń w przestrzeni użytkownika
Group:		Base
Requires(post,postun):	/sbin/ldconfig
Requires(post,preun,postun):	systemd-units >= 1:234
Requires:	device-mapper-libs = %{version}-%{release}
Requires:	systemd-units >= 1:234

%description -n device-mapper
The goal of this driver is to support volume management. The driver
enables the definition of new block devices composed of ranges of
sectors of existing devices. This can be used to define disk
partitions - or logical volumes. This light-weight kernel component
can support user-space tools for logical volume management.

%description -n device-mapper -l pl.UTF-8
Celem tego sterownika jest obsługa zarządzania wolumenami. Sterownik
włącza definiowanie nowych urządzeń blokowych złożonych z przedziałów
sektorów na istniejących urządzeniach. Może to być wykorzystane do
definiowania partycji na dysku lub logicznych wolumenów. Ten lekki
składnik jądra może wspierać działające w przestrzeni użytkownika
narzędzia do zarządzania logicznymi wolumenami.

%package -n device-mapper-libs
Summary:	Device-mapper shared libraries
Summary(pl.UTF-8):	Biblioteki współdzielone device-mappera
Group:		Libraries
Requires:	libblkid >= 2.24
Requires:	udev-libs >= 1:176
Obsoletes:	python-lvm < 2.03
Obsoletes:	python3-lvm < 2.03
Conflicts:	device-mapper < 2.02.119-1

%description -n device-mapper-libs
Device-mapper shared libraries.

%description -n device-mapper-libs -l pl.UTF-8
Biblioteki współdzielone device-mappera.

%package -n device-mapper-devel
Summary:	Header files for device-mapper libraries
Summary(pl.UTF-8):	Pliki nagłówkowe bibliotek device-mappera
Group:		Development/Libraries
Requires:	device-mapper-libs = %{version}-%{release}
Requires:	libblkid-devel >= 2.24
%if %{with selinux}
Requires:	libselinux-devel
Requires:	libsepol-devel
%endif
Requires:	udev-devel >= 1:176
Obsoletes:	device-mapper-dietlibc < 2.03

%description -n device-mapper-devel
Header files for device-mapper libraries.

%description -n device-mapper-devel -l pl.UTF-8
Pliki nagłówkowe bibliotek device-mappera.

%package -n device-mapper-static
Summary:	Static devmapper library
Summary(pl.UTF-8):	Statyczna biblioteka devmapper
License:	LGPL v2.1
Group:		Development/Libraries
Requires:	device-mapper-devel = %{version}-%{release}

%description -n device-mapper-static
Static devmapper library.

%description -n device-mapper-static -l pl.UTF-8
Statyczna biblioteka devmapper.

%package -n device-mapper-initrd
Summary:	Userspace support for the device-mapper - initrd version
Summary(pl.UTF-8):	Wsparcie dla mapowania urządzeń w przestrzeni użytkownika - wersja dla initrd
Group:		Base
Obsoletes:	device-mapper-initrd-devel < 2
Conflicts:	geninitrd < 10000.10

%description -n device-mapper-initrd
The goal of this driver is to support volume management. The driver
enables the definition of new block devices composed of ranges of
sectors of existing devices. This can be used to define disk
partitions - or logical volumes. This light-weight kernel component
can support user-space tools for logical volume management.

This package contains dmsetup program linked staticaly for use in
initrd.

%description -n device-mapper-initrd -l pl.UTF-8
Celem tego sterownika jest obsługa zarządzania wolumenami. Sterownik
włącza definiowanie nowych urządzeń blokowych złożonych z przedziałów
sektorów na istniejących urządzeniach. Może to być wykorzystane do
definiowania partycji na dysku lub logicznych wolumenów. Ten lekki
składnik jądra może wspierać działające w przestrzeni użytkownika
narzędzia do zarządzania logicznymi wolumenami.

Ten pakiet zawiera program dmsetup skonsolidowany statycznie na
potrzeby initrd.

%prep
%setup -q -n LVM2.%{version}
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1

%build
%{__aclocal}
%{__autoconf}

%if %{with initrd}
%configure \
	%{?debug:--enable-debug} \
	--disable-blkid_wiping \
	--disable-nls \
	--disable-readline \
	%{!?with_selinux:--disable-selinux} \
	--disable-silent-rules \
	--enable-static_link \
	--with-optimisation="%{rpmcflags} -Os"

echo 'STATIC_LIBS += %{?with_selinux:-lpcre} -lpthread -lm' >> libdm/make.tmpl

%{__make} -j1 -C lib liblvm-internal.a

%{__make} -j1 -C libdm ioctl/libdevmapper.a \
	V=1

%{__make} -j1 -C libdaemon/client libdaemonclient.a

%{__make} -j1 -C libdm/dm-tools dmsetup.static \
	V=1

%{__make} -j1 base/libbase.a device_mapper/libdevice-mapper.a

%{__make} -j1 -C tools lvm.static \
	LIBS="%{?with_selinux:-lpcre} -lpthread -lm" \
	SHELL=/bin/bash \
	interfacebuilddir=../libdm/ioctl

%{__mv} tools/lvm.static initrd-lvm
%{__mv} libdm/dm-tools/dmsetup.static initrd-dmsetup

# check if tools works
for tool in initrd-lvm initrd-dmsetup; do
	LVM_SYSTEM_DIR=$(pwd) ./$tool help && rc=$? || rc=$?
	if [ $rc -gt 127 ]; then
		echo >&2 "Unexpected failure (exit status: $rc) from $tool. Does this tool work?!"
		exit 1
	fi
done

%{__make} clean

unset CC
%endif

%configure \
	--enable-cache_check_needs_check \
	--enable-cmdlib \
%if %{with cluster}
	--enable-cmirrord \
%endif
	%{?with_lvmdbusd:--enable-dbus-service --enable-notify-dbus} \
	%{?debug:--enable-debug} \
	--enable-dmeventd \
	--enable-dmfilemapd \
	--enable-fsadm \
%if %{with lvmlockd}
	%{?with_cluster:--enable-lvmlockd-dlm} \
	%{?with_sanlock:--enable-lvmlockd-sanlock} \
%endif
	--enable-lvmpolld \
	--enable-ocf \
	--enable-pkgconfig \
	--enable-readline \
	%{!?with_selinux:--disable-selinux} \
	--disable-silent-rules \
	--enable-thin_check_needs_check \
	--enable-udev_sync \
	--enable-udev_rules \
	--with-cache=internal \
	--with-cache-check=/usr/sbin/cache_check \
	--with-cache-dump=/usr/sbin/cache_dump \
	--with-cache-repair=/usr/sbin/cache_repair \
	--with-cache-restore=/usr/sbin/cache_restore \
	--with-default-locking-dir=/var/lock/lvm \
	--with-dmeventd-path=%{_sbindir}/dmeventd \
	--with-interface=ioctl \
	--with-libexecdir=%{_libexecdir} \
	--with-mirrors=internal \
	--with-optimisation="%{rpmcflags}" \
	--with-snapshots=internal \
	--with-systemdsystemunitdir=%{systemdunitdir} \
	--with-tmpfilesdir=%{systemdtmpfilesdir} \
	--with-thin=internal \
	--with-thin-check=/usr/sbin/thin_check \
	--with-thin-dump=/usr/sbin/thin_dump \
	--with-thin-repair=/usr/sbin/thin_repair \
	--with-thin-restore=/usr/sbin/thin_restore \
	--with-udev-prefix=/ \
	--with-usrlibdir=%{_libdir} \
	--with-vdo=internal --with-vdo-format=%{_bindir}/vdoformat \
	--with-writecache=internal

# no --enable-nls: no translations exist, broken

# use bash because of "set -o pipefail"
# V=1 still used because of missing --disable-silent-rules support in libdm (as of 2.03.09)
%{__make} -j1 \
	SHELL=/bin/bash \
	V=1
%{__make} -j1 -C libdm \
	LIB_STATIC=libdevmapper.a \
	V=1

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/%{_lib},%{_sysconfdir}/lvm,/etc/sysconfig,/var/lock/lvm/subsys}

%{__make} install install_system_dirs install_systemd_units install_systemd_generators install_initscripts install_tmpfiles_configuration \
	DESTDIR=$RPM_BUILD_ROOT \
	PYTHON_PREFIX=%{_prefix} \
	OWNER="" \
	GROUP=""

%{__make} -C scripts install_tmpfiles_configuration \
	DESTDIR=$RPM_BUILD_ROOT

%{__mv} $RPM_BUILD_ROOT%{_libdir}/lib*.so.* $RPM_BUILD_ROOT/%{_lib}
for lib in $RPM_BUILD_ROOT/%{_lib}/lib*.so.*; do
	lib=$(echo $lib | sed -e "s#$RPM_BUILD_ROOT##g")
	slib=$(basename $lib | sed -e 's#\.so\..*#.so#g')
	ln -sf $lib $RPM_BUILD_ROOT%{_libdir}/$slib
done

touch $RPM_BUILD_ROOT%{_sysconfdir}/lvm/lvm.conf

%if %{with initrd}
install -d $RPM_BUILD_ROOT%{_libdir}/initrd
install -p initrd-lvm $RPM_BUILD_ROOT%{_libdir}/initrd/lvm
install -p initrd-dmsetup $RPM_BUILD_ROOT%{_libdir}/initrd/dmsetup
%endif

cp -a libdm/libdevmapper.a $RPM_BUILD_ROOT%{_libdir}

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add lvm2-monitor
%service lvm2-monitor restart
%systemd_post lvm2-monitor.service
/sbin/chkconfig --add blk-availability
%if %{with lvmpolld}
%systemd_post lvm2-lvmpolld.socket
%endif

%preun
%systemd_preun lvm2-monitor.service
%if %{with lvmpolld}
%systemd_preun lvm2-lvmpolld.socket
%endif

%postun
if [ "$1" = "0" ]; then
	%service lvm2-monitor stop
	/sbin/chkconfig --del lvm2-monitor
	#no service blk-availability stop
	/sbin/chkconfig --del blk-availability
fi
%systemd_reload

%triggerpostun -- %{name} < 2.02.94-1
%systemd_trigger lvm2-monitor.service

%post -n device-mapper
%systemd_post dm-event.socket

%preun -n device-mapper
%systemd_preun dm-event.socket dm-event.service

%postun -n device-mapper
%systemd_reload

%triggerpostun -n device-mapper -- device-mapper < 2.02.94-1
%systemd_trigger dm-event.socket

%post	-n device-mapper-libs -p /sbin/ldconfig
%postun	-n device-mapper-libs -p /sbin/ldconfig

%post dbusd
%systemd_post lvm2-lvmdbusd.service

%preun dbusd
%systemd_preun lvm2-lvmdbusd.service

%postun dbusd
%systemd_reload

%post lockd
%systemd_post lvmlockd.service lvmlocks.service

%preun lockd
%systemd_preun lvmlockd.service lvmlocks.service

%postun lockd
%systemd_reload

%files
%defattr(644,root,root,755)
%doc README WHATS_NEW doc/*
%attr(755,root,root) %{_sbindir}/blkdeactivate
%attr(755,root,root) %{_sbindir}/fsadm
%attr(755,root,root) %{_sbindir}/lvchange
%attr(755,root,root) %{_sbindir}/lvconvert
%attr(755,root,root) %{_sbindir}/lvcreate
%attr(755,root,root) %{_sbindir}/lvdisplay
%attr(755,root,root) %{_sbindir}/lvextend
%attr(755,root,root) %{_sbindir}/lvm
%attr(755,root,root) %{_sbindir}/lvm_import_vdo
%attr(755,root,root) %{_sbindir}/lvmconfig
%attr(755,root,root) %{_sbindir}/lvmdevices
%attr(755,root,root) %{_sbindir}/lvmdiskscan
%attr(755,root,root) %{_sbindir}/lvmdump
%attr(755,root,root) %{_sbindir}/lvmsadc
%attr(755,root,root) %{_sbindir}/lvmsar
%attr(755,root,root) %{_sbindir}/lvreduce
%attr(755,root,root) %{_sbindir}/lvremove
%attr(755,root,root) %{_sbindir}/lvrename
%attr(755,root,root) %{_sbindir}/lvresize
%attr(755,root,root) %{_sbindir}/lvs
%attr(755,root,root) %{_sbindir}/lvscan
%attr(755,root,root) %{_sbindir}/pvchange
%attr(755,root,root) %{_sbindir}/pvck
%attr(755,root,root) %{_sbindir}/pvcreate
%attr(755,root,root) %{_sbindir}/pvdisplay
%attr(755,root,root) %{_sbindir}/pvmove
%attr(755,root,root) %{_sbindir}/pvremove
%attr(755,root,root) %{_sbindir}/pvresize
%attr(755,root,root) %{_sbindir}/pvs
%attr(755,root,root) %{_sbindir}/pvscan
%attr(755,root,root) %{_sbindir}/vgcfgbackup
%attr(755,root,root) %{_sbindir}/vgcfgrestore
%attr(755,root,root) %{_sbindir}/vgchange
%attr(755,root,root) %{_sbindir}/vgck
%attr(755,root,root) %{_sbindir}/vgconvert
%attr(755,root,root) %{_sbindir}/vgcreate
%attr(755,root,root) %{_sbindir}/vgdisplay
%attr(755,root,root) %{_sbindir}/vgexport
%attr(755,root,root) %{_sbindir}/vgextend
%attr(755,root,root) %{_sbindir}/vgimport
%attr(755,root,root) %{_sbindir}/vgimportclone
%attr(755,root,root) %{_sbindir}/vgimportdevices
%attr(755,root,root) %{_sbindir}/vgmerge
%attr(755,root,root) %{_sbindir}/vgmknodes
%attr(755,root,root) %{_sbindir}/vgreduce
%attr(755,root,root) %{_sbindir}/vgremove
%attr(755,root,root) %{_sbindir}/vgrename
%attr(755,root,root) %{_sbindir}/vgs
%attr(755,root,root) %{_sbindir}/vgscan
%attr(755,root,root) %{_sbindir}/vgsplit
%attr(755,root,root) %{_libexecdir}/lvresize_fs_helper
%{_mandir}/man5/lvm.conf.5*
%{_mandir}/man7/lvmautoactivation.7*
%{_mandir}/man7/lvmcache.7*
%{_mandir}/man7/lvmraid.7*
%{_mandir}/man7/lvmreport.7*
%{_mandir}/man7/lvmsystemid.7*
%{_mandir}/man7/lvmthin.7*
%{_mandir}/man7/lvmvdo.7*
%{_mandir}/man8/blkdeactivate.8*
%{_mandir}/man8/fsadm.8*
%{_mandir}/man8/lvchange.8*
%{_mandir}/man8/lvconvert.8*
%{_mandir}/man8/lvcreate.8*
%{_mandir}/man8/lvdisplay.8*
%{_mandir}/man8/lvextend.8*
%{_mandir}/man8/lvm-config.8*
%{_mandir}/man8/lvm-dumpconfig.8*
%{_mandir}/man8/lvm-fullreport.8*
%{_mandir}/man8/lvm-lvpoll.8*
%{_mandir}/man8/lvm.8*
%{_mandir}/man8/lvm_import_vdo.8*
%{_mandir}/man8/lvmconfig.8*
%{_mandir}/man8/lvmdevices.8*
%{_mandir}/man8/lvmdiskscan.8*
%{_mandir}/man8/lvmdump.8*
%{_mandir}/man8/lvmsadc.8*
%{_mandir}/man8/lvmsar.8*
%{_mandir}/man8/lvreduce.8*
%{_mandir}/man8/lvremove.8*
%{_mandir}/man8/lvrename.8*
%{_mandir}/man8/lvresize.8*
%{_mandir}/man8/lvs.8*
%{_mandir}/man8/lvscan.8*
%{_mandir}/man8/pvchange.8*
%{_mandir}/man8/pvck.8*
%{_mandir}/man8/pvcreate.8*
%{_mandir}/man8/pvdisplay.8*
%{_mandir}/man8/pvmove.8*
%{_mandir}/man8/pvremove.8*
%{_mandir}/man8/pvresize.8*
%{_mandir}/man8/pvs.8*
%{_mandir}/man8/pvscan.8*
%{_mandir}/man8/vgcfgbackup.8*
%{_mandir}/man8/vgcfgrestore.8*
%{_mandir}/man8/vgchange.8*
%{_mandir}/man8/vgck.8*
%{_mandir}/man8/vgconvert.8*
%{_mandir}/man8/vgcreate.8*
%{_mandir}/man8/vgdisplay.8*
%{_mandir}/man8/vgexport.8*
%{_mandir}/man8/vgextend.8*
%{_mandir}/man8/vgimport.8*
%{_mandir}/man8/vgimportclone.8*
%{_mandir}/man8/vgimportdevices.8*
%{_mandir}/man8/vgmerge.8*
%{_mandir}/man8/vgmknodes.8*
%{_mandir}/man8/vgreduce.8*
%{_mandir}/man8/vgremove.8*
%{_mandir}/man8/vgrename.8*
%{_mandir}/man8/vgs.8*
%{_mandir}/man8/vgscan.8*
%{_mandir}/man8/vgsplit.8*
%attr(750,root,root) %dir %{_sysconfdir}/lvm
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/lvm/lvm.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/lvm/lvmlocal.conf
%attr(750,root,root) %dir %{_sysconfdir}/lvm/profile
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/lvm/profile/cache-mq.profile
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/lvm/profile/cache-smq.profile
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/lvm/profile/command_profile_template.profile
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/lvm/profile/metadata_profile_template.profile
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/lvm/profile/thin-generic.profile
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/lvm/profile/thin-performance.profile
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/lvm/profile/vdo-small.profile
%{systemdtmpfilesdir}/lvm2.conf
%{systemdunitdir}/blk-availability.service
%{systemdunitdir}/lvm-devices-import.path
%{systemdunitdir}/lvm-devices-import.service
%{systemdunitdir}/lvm2-monitor.service
%dir %{_sysconfdir}/lvm/cache
%ghost %{_sysconfdir}/lvm/cache/.cache
%attr(754,root,root) /etc/rc.d/init.d/blk-availability
%attr(754,root,root) /etc/rc.d/init.d/lvm2-monitor
%attr(700,root,root) %dir /run/lvm
%attr(700,root,root) %dir /var/lock/lvm
%attr(700,root,root) %dir /var/lock/lvm/subsys
%if %{with lvmpolld}
%attr(755,root,root) %{_sbindir}/lvmpolld
%attr(754,root,root) /etc/rc.d/init.d/lvm2-lvmpolld
%{systemdunitdir}/lvm2-lvmpolld.service
%{systemdunitdir}/lvm2-lvmpolld.socket
%{_mandir}/man8/lvmpolld.8*
%endif

%if %{with cluster}
%files cmirrord
%defattr(644,root,root,755)
%attr(755,root,root) %{_usrsbindir}/cmirrord
%attr(754,root,root) /etc/rc.d/init.d/cmirrord
%{systemdunitdir}/lvm2-cmirrord.service
%{_mandir}/man8/cmirrord.8*
%endif

%if %{with lvmdbusd}
%files dbusd
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/lvmdbusd
%{py3_sitescriptdir}/lvmdbusd
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/lvm/profile/lvmdbusd.profile
%config(noreplace) %verify(not md5 mtime size) /etc/dbus-1/system.d/com.redhat.lvmdbus1.conf
%{_datadir}/dbus-1/system-services/com.redhat.lvmdbus1.service
%{systemdunitdir}/lvm2-lvmdbusd.service
%{_mandir}/man8/lvmdbusd.8*
%endif

%if %{with lvmlockd}
%files lockd
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/lvmlockctl
%attr(755,root,root) %{_sbindir}/lvmlockd
%{systemdunitdir}/lvmlockd.service
%{systemdunitdir}/lvmlocks.service
%{_mandir}/man8/lvmlockctl.8*
%{_mandir}/man8/lvmlockd.8*
%endif

%files resource-agents
%defattr(644,root,root,755)
%dir %{_prefix}/lib/ocf/resource.d/lvm2
%attr(755,root,root) %{_prefix}/lib/ocf/resource.d/lvm2/VolumeGroup

%files -n device-mapper
%defattr(644,root,root,755)
%doc *_DM
%{systemdunitdir}/dm-event.service
%{systemdunitdir}/dm-event.socket
/lib/udev/rules.d/10-dm.rules
/lib/udev/rules.d/11-dm-lvm.rules
/lib/udev/rules.d/13-dm-disk.rules
/lib/udev/rules.d/69-dm-lvm.rules
/lib/udev/rules.d/95-dm-notify.rules
%attr(755,root,root) %{_sbindir}/dmeventd
%attr(755,root,root) %{_sbindir}/dmfilemapd
%attr(755,root,root) %{_sbindir}/dmsetup
%attr(755,root,root) %{_sbindir}/dmstats
%attr(755,root,root) %{_libdir}/libdevmapper-event-lvm2mirror.so
%attr(755,root,root) %{_libdir}/libdevmapper-event-lvm2raid.so
%attr(755,root,root) %{_libdir}/libdevmapper-event-lvm2snapshot.so
%attr(755,root,root) %{_libdir}/libdevmapper-event-lvm2thin.so
%attr(755,root,root) %{_libdir}/libdevmapper-event-lvm2vdo.so
%dir %{_libdir}/device-mapper
%attr(755,root,root) %{_libdir}/device-mapper/libdevmapper-event-lvm2mirror.so
%attr(755,root,root) %{_libdir}/device-mapper/libdevmapper-event-lvm2raid.so
%attr(755,root,root) %{_libdir}/device-mapper/libdevmapper-event-lvm2snapshot.so
%attr(755,root,root) %{_libdir}/device-mapper/libdevmapper-event-lvm2thin.so
%attr(755,root,root) %{_libdir}/device-mapper/libdevmapper-event-lvm2vdo.so
%{_mandir}/man8/dmfilemapd.8*
%{_mandir}/man8/dmsetup.8*
%{_mandir}/man8/dmstats.8*
%{_mandir}/man8/dmeventd.8*

%files -n device-mapper-libs
%defattr(644,root,root,755)
%attr(755,root,root) /%{_lib}/libdevmapper.so.*.*
%attr(755,root,root) /%{_lib}/libdevmapper-event.so.*.*
%attr(755,root,root) /%{_lib}/libdevmapper-event-lvm2.so.*.*
%attr(755,root,root) /%{_lib}/liblvm2cmd.so.*.*

%files -n device-mapper-devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libdevmapper.so
%attr(755,root,root) %{_libdir}/libdevmapper-event.so
%attr(755,root,root) %{_libdir}/libdevmapper-event-lvm2.so
%attr(755,root,root) %{_libdir}/liblvm2cmd.so
%{_includedir}/libdevmapper.h
%{_includedir}/libdevmapper-event.h
%{_includedir}/lvm2cmd.h
%{_pkgconfigdir}/devmapper.pc
%{_pkgconfigdir}/devmapper-event.pc

%files -n device-mapper-static
%defattr(644,root,root,755)
%{_libdir}/libdevmapper.a

%if %{with initrd}
%files -n device-mapper-initrd
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/initrd/dmsetup

%files initrd
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/initrd/lvm
%endif
