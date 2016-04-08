# TODO
# - vgscan --ignorelocking failure creates /var/lock/lvm (even if /var is not yet mounted)
# - spec default value for --with-replicators (=internal/shared/none, configure default is none)?
#   (also internal vs shared for lvm1,pool,cluster,snapshots,mirrors,raid,replicators,thin,cache;
#    note: dmeventd requires mirrors=internal)
#
# Conditional build:
# - initrd stuff
%bcond_with	initrd		# build initrd version
%bcond_without	uClibc		# link initrd version with uClibc
%bcond_with	dietlibc	# link initrd version with dietlibc
%bcond_with	glibc		# link initrd version with static GLIBC
# - functionality
%bcond_without  cluster		# disable all cluster support (clvmd&cmirrord)
%bcond_without	lvmetad		# lvmetad (and lvmlockd)
%bcond_without	lvmdbusd	# lvmdbusd
%bcond_without	lvmpolld	# lvmpolld (and lvmlockd)
%bcond_without	lvmlockd	# lvmlockd
%bcond_with	sanlock		# sanlock support in lvmlockd
%bcond_with	replicator	# internal replicator support
# - additional features
%bcond_without	selinux		# SELinux support
# - bindings
%bcond_without	python		# Python bindings
%bcond_without	python2		# Python 2 binding
%bcond_without	python3		# Python 3 binding and lvmdbusd

# lvmlockd requires lvmetad and lvmpolld
%if %{without lvmetad} || %{without lvmpolld}
%undefine	with_lvmpolld
%endif

# only glibc possible on SPARC
%ifarch sparc sparcv9 sparc64
%define		with_glibc 1
%endif
# if one of the *libc is enabled disable default dietlibc
%if %{with dietlibc} && %{with uClibc}
%undefine	with_dietlibc
%endif
# with glibc disables default dietlibc
%if %{with glibc} && %{with dietlibc}
%undefine	with_dietlibc
%endif
# fallback is glibc if neither alternatives are enabled
%if %{without dietlibc} && %{without uClibc}
%define		with_glibc	1
%endif
# for convenience
%if %{without python}
%undefine	with_python2
%undefine	with_python3
%endif
%if %{without python3}
%undefine	with_lvmdbusd
%endif

Summary:	The new version of Logical Volume Manager for Linux
Summary(pl.UTF-8):	Nowa wersja Logical Volume Managera dla Linuksa
Name:		lvm2
Version:	2.02.149
Release:	1
License:	GPL v2 and LGPL v2.1
Group:		Applications/System
Source0:	ftp://sources.redhat.com/pub/lvm2/LVM2.%{version}.tgz
# Source0-md5:	39f766faa1cf95fcdf80868839350147
Source2:	clvmd.service
Source3:	clvmd.sysconfig
Patch0:		%{name}-selinux.patch
Patch1:		%{name}-diet.patch
Patch2:		device-mapper-dmsetup-export.patch
Patch3:		%{name}-pld_init.patch
Patch4:		dl-dlsym.patch
Patch6:		%{name}-lvm_path.patch
Patch7:		%{name}-sd_notify.patch
Patch8:		%{name}-clvmd_cmd_timeout.patch
Patch9:		device-mapper-dmsetup-deps-export.patch
Patch10:	%{name}-replicator.patch
Patch11:	%{name}-thin.patch
URL:		http://www.sourceware.org/lvm2/
BuildRequires:	autoconf >= 2.69
BuildRequires:	automake
# for /run detection
BuildRequires:	filesystem >= 3.0-43
BuildRequires:	libblkid-devel >= 2.24
%{?with_selinux:BuildRequires:	libselinux-devel >= 1.10}
%{?with_selinux:BuildRequires:	libsepol-devel}
BuildRequires:	ncurses-devel
BuildRequires:	pkgconfig
%{?with_python2:BuildRequires:	python-devel >= 2}
%{?with_python3:BuildRequires:	python3-devel >= 1:3.2}
%if %{with lvmdbusd}
BuildRequires:	python3-dbus
BuildRequires:	python3-pyudev
%endif
BuildRequires:	readline-devel
BuildRequires:	rpmbuild(macros) >= 1.647
%{?with_sanlock:BuildRequires:	sanlock-devel >= 3.3.0}
BuildRequires:	systemd-devel >= 1:205
BuildRequires:	udev-devel >= 1:176
%if %{with initrd}
%if %{with dietlibc}
BuildRequires:	dietlibc-static >= 2:0.32-7
BuildConflicts:	device-mapper-dietlibc
%endif
%if %{with glibc}
%{?with_selinux:BuildRequires:	libselinux-static}
%{?with_selinux:BuildRequires:	libsepol-static}
%endif
%{?with_glibc:BuildRequires:	glibc-static}
%{?with_uClibc:BuildRequires:	uClibc-static >= 2:0.9.29}
%endif
%if %{with cluster}
BuildRequires:	corosync-devel
BuildRequires:	dlm-devel >= 3.99.5
%endif
Requires(post,preun,postun):	systemd-units >= 38
Requires(post,postun):	/sbin/chkconfig
Requires:	device-mapper >= %{version}-%{release}
%{?with_selinux:Requires:	libselinux >= 1.10}
Requires:	systemd-units >= 38
# doesn't work with 2.4 kernels
Requires:	uname(release) >= 2.6
Suggests:	thin-provisioning-tools >= 0.5.4
Obsoletes:	lvm
Obsoletes:	lvm2-systemd
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sbindir	/sbin
%define		_usrsbindir	/usr/sbin

# changing CFLAGS in the middle confuses confcache
%undefine	configure_cache

# borken on AC
%define		filterout_ld	-Wl,--as-needed

# causes: undefined reference to `__stack_chk_fail_local'
%define		filterout_c	-fstack-protector

# for some reason known only to rpm there must be "\\|" not "\|" here
%define		dietarch	%(echo %{_target_cpu} | sed -e 's/i.86\\|pentium.\\|athlon/i386/;s/amd64/x86_64/;s/armv.*/arm/')
%define		dietlibdir	%{_prefix}/lib/dietlibc/lib-%{dietarch}

%define		skip_post_check_so	'.*libdevmapper-event-lvm2.so.*'

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

%package clvmd
Summary:	Cluster LVM daemon
Summary(pl.UTF-8):	Demon clustra LVM
Group:		Applications/System
Requires:	%{name} = %{version}-%{release}

%description clvmd
clvmd is the daemon that distributes LVM metadata updates around a
cluster. It must be running on all nodes in the cluster and will give
an error if a node in the cluster does not have this daemon running.

%description clvmd -l pl.UTF-8
clvmd to demon który rozprowadza zmiany meta-danych LVM po klastrze.
Mysi działać na wszystkich węzłach klastra i zgłosi błąd gdy jakiś
węzeł w klastrze nie ma tego demona uruchomionego.

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

%description cmirrord
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
Requires(post,preun,postun):	systemd-units >= 38
Requires:	%{name} = %{version}-%{release}
Requires:	python3-dbus
Requires:	python3-pyudev
Requires:	python3-pygobject3 >= 3

%description dbusd
Daemon for access to LVM2 functionality through a D-Bus interface.

%description dbusd -l pl.UTF-8
Demon umożliwiający dostęp do funkcjonalności LVM2 poprzez interfejs
D-Bus.

%package lockd
Summary:	LVM2 locking daemon
Summary(pl.UTF-8):	Demon blokad LVM2
Group:		Daemons
Requires(post,preun,postun):	systemd-units >= 38
Requires:	%{name} = %{version}-%{release}
%{?with_sanlock:Requires:	sanlock-libs >= 3.3.0}
%{?with_cluster:Requires:	dlm-libs >= 3.99.5}

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

%package -n python-lvm
Summary:	Python 2 interface to LVM2
Summary(pl.UTF-8):	Interfejs Pythona 2 do LVM2
Group:		Libraries/Python
Requires:	device-mapper-libs = %{version}-%{release}

%description -n python-lvm
Python 2 interface to LVM2.

%description -n python-lvm -l pl.UTF-8
Interfejs Pythona 2 do LVM2.

%package -n python3-lvm
Summary:	Python 3 interface to LVM2
Summary(pl.UTF-8):	Interfejs Pythona 3 do LVM2
Group:		Libraries/Python
Requires:	device-mapper-libs = %{version}-%{release}

%description -n python3-lvm
Python 3 interface to LVM2.

%description -n python3-lvm -l pl.UTF-8
Interfejs Pythona 3 do LVM2.

%package -n device-mapper
Summary:	Userspace support for the device-mapper
Summary(pl.UTF-8):	Wsparcie dla mapowania urządzeń w przestrzeni użytkownika
Group:		Base
Requires(post,postun):	/sbin/ldconfig
Requires(post,preun,postun):	systemd-units >= 38
Requires:	device-mapper-libs = %{version}-%{release}
Requires:	systemd-units >= 38

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
Conflicts:	device-mapper < 2.02.119-1
Requires:	libblkid >= 2.24
Requires:	udev-libs >= 1:176

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

%package -n device-mapper-dietlibc
Summary:	Static devmapper library built with dietlibc
Summary(pl.UTF-8):	Statyczna biblioteka devmapper zbudowana z dietlibc
License:	LGPL v2.1
Group:		Development/Libraries
Requires:	device-mapper-devel = %{version}-%{release}

%description -n device-mapper-dietlibc
Static devmapper library built with dietlibc.

%description -n device-mapper-dietlibc -l pl.UTF-8
Statyczna biblioteka devmapper zbudowana z dietlibc.

%package -n device-mapper-initrd
Summary:	Userspace support for the device-mapper - initrd version
Summary(pl.UTF-8):	Wsparcie dla mapowania urządzeń w przestrzeni użytkownika - wersja dla initrd
Group:		Base
Obsoletes:	device-mapper-initrd-devel
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
%{?with_selinux:%patch0 -p1}
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1
%patch11 -p1

# do not force --export-symbol linker option for e.g. statically linked executables
# -rdynamic compiler option drives linker in the right way.
%{__sed} -i -e 's#-Wl,--export-dynamic#-rdynamic#g' configure.in

%build
%if %{with initrd}
echo Using %{?with_glibc:GLIBC} %{?with_uClibc:uClibc} %{?with_dietlibc:diet} for initrd
%endif
cp -f /usr/share/automake/config.sub autoconf
%{__aclocal}
%{__autoconf}

%if %{with initrd}
%{?with_glibc:export CC="%{__cc}"}
%{?with_uClibc:export CC="%{_target_cpu}-uclibc-gcc"}
%{?with_dietlibc:cc="%{__cc}"; export CC="diet ${cc#ccache }"}

%configure \
	ac_cv_lib_dl_dlopen=no \
	%{?with_uClibc:ac_cv_func_siginterrupt=no} \
	%{?debug:--enable-debug} \
	--disable-nls \
	--disable-readline \
	--enable-selinux%{!?with_glibc:=no} \
	--enable-static_link \
	--with-lvm1=internal \
	--with-optimisation="%{rpmcflags} -Os"
# glibc version links with normal static libdevicemapper which has selinux enabled
# and we need to keep these in sync between device-mapper and lvm2

%{__sed} -i -e 's#rpl_malloc#malloc#g' lib/misc/configure.h
%{__sed} -i -e 's#rpl_realloc#realloc#g' lib/misc/configure.h

%{__make} -j1 -C include
%{__make} -j1 -C lib LIB_SHARED= VERSIONED_SHLIB=
%{__make} -j1 -C libdm LIB_SHARED= VERSIONED_SHLIB=
%{__make} -j1 -C libdaemon/client LIB_SHARED= VERSIONED_SHLIB=
%{__make} -j1 -C tools dmsetup.static lvm.static %{?with_dietlibc:DIETLIBC_LIBS="-lcompat"}
%{__mv} tools/lvm.static initrd-lvm
%{__mv} tools/dmsetup.static initrd-dmsetup

# check if tools works
for tool in initrd-lvm initrd-dmsetup; do
	LVM_SYSTEM_DIR=$(pwd) ./$tool help && rc=$? || rc=$?
	if [ $rc -gt 127 ]; then
		echo >&2 "Unexpected failure (exit status: $rc) from $tool. Does this tool work?!"
		exit 1
	fi
done

%{?with_dietlibc:%{__mv} libdm/ioctl/libdevmapper.a diet-libdevmapper.a}
%{__make} clean

unset CC
%endif

%configure \
	--enable-applib \
	--enable-cache_check_needs_check \
	--enable-cmdlib \
	%{?with_lvmdbusd:--enable-dbus-service} \
	%{?debug:--enable-debug} \
	--enable-dmeventd \
	--enable-fsadm \
%if %{with lvmlockd}
	%{?with_cluster:--enable-lockd-dlm} \
	%{?with_sanlock:--enable-lockd-sanlock} \
%endif
	%{?with_lvmetad:--enable-lvmetad} \
	--enable-ocf \
	%{?with_python2:--enable-python2_bindings} \
	%{?with_python3:--enable-python3_bindings} \
	--enable-readline \
	%{!?with_selinux:--disable-selinux} \
	--enable-pkgconfig \
	--enable-thin_check_needs_check \
	--enable-udev_sync \
	--enable-udev_rules \
	--with-cache=internal \
	--with-cache-check=/usr/sbin/cache_check \
	--with-cache-dump=/usr/sbin/cache_dump \
	--with-cache-repair=/usr/sbin/cache_repair \
	--with-cache-restore=/usr/sbin/cache_restore \
	--with-cluster=internal \
%if %{with cluster}
	--with-clvmd=corosync \
	--enable-cmirrord \
%endif
	--with-dmeventd-path=%{_sbindir}/dmeventd \
	--with-interface=ioctl \
	--with-lvm1=internal \
	--with-mirrors=internal \
	--with-optimisation="%{rpmcflags}" \
	--with-pool=internal \
	%{?with_replicator:--with-replicators=internal} \
	--with-snapshots=internal \
	--with-systemdsystemunitdir=%{systemdunitdir} \
	--with-tmpfilesdir=%{systemdtmpfilesdir} \
	--with-thin=internal \
	--with-thin-check=/usr/sbin/thin_check \
	--with-thin-dump=/usr/sbin/thin_dump \
	--with-thin-repair=/usr/sbin/thin_repair \
	--with-thin-restore=/usr/sbin/thin_restore \
	--with-udev-prefix=/ \
	--with-usrlibdir=%{_libdir}

%{__make} -j1
%{__make} -j1 -C libdm LIB_STATIC=libdevmapper.a

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/%{_lib},%{_sysconfdir}/lvm,/etc/sysconfig}
%{?with_dietlibc:install -d $RPM_BUILD_ROOT%{dietlibdir}}

%{__make} install install_system_dirs install_systemd_units install_initscripts install_tmpfiles_configuration \
	DESTDIR=$RPM_BUILD_ROOT \
	OWNER="" \
	GROUP=""

%{__make} -C scripts install_tmpfiles_configuration \
	DESTDIR=$RPM_BUILD_ROOT \

%if %{with cluster}
cp -p %{SOURCE2} $RPM_BUILD_ROOT%{systemdunitdir}/clvmd.service
cp -p %{SOURCE3} $RPM_BUILD_ROOT/etc/sysconfig/clvmd
%endif

mv $RPM_BUILD_ROOT%{_libdir}/lib*.so.* $RPM_BUILD_ROOT/%{_lib}
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

%{?with_dietlibc:cp -a diet-libdevmapper.a $RPM_BUILD_ROOT%{dietlibdir}/libdevmapper.a}
%endif

cp -a libdm/libdevmapper.a $RPM_BUILD_ROOT%{_libdir}

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add lvm2-monitor
%service lvm2-monitor restart
%systemd_post lvm2-monitor.service
/sbin/chkconfig --add blk-availability
# no service blk-availability restart
%systemd_post blk-availability.service
%if %{with lvmetad}
%systemd_post lvm2-lvmetad.socket
%endif
%if %{with lvmpolld}
%systemd_post lvm2-lvmpolld.socket
%endif

%preun
%systemd_preun lvm2-monitor.service
%systemd_preun blk-availability.service
%if %{with lvmetad}
%systemd_preun lvm2-lvmetad.socket
%endif
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

%post clvmd
/sbin/chkconfig --add clvmd
# no service restart - it breaks current locks!
export NORESTART=1
%systemd_post clvmd.service
# re-exec instead
/usr/sbin/clvmd -S 2>/dev/null || :

%preun clvmd
%systemd_preun clvmd.service
if [ "$1" = "0" ]; then
	%service clvmd stop
	/sbin/chkconfig --del clvmd
fi

%postun clvmd
%systemd_reload

%post dbusd
%systemd_post lvm2-lvmdbusd.service

%preun dbusd
%systemd_preun lvm2-lvmdbusd.service

%postun dbusd
%systemd_reload

%post lockd
%systemd_post lvm2-lvmlockd.service lvm2-lvmlocking.service

%preun lockd
%systemd_preun lvm2-lvmlockd.service lvm2-lvmlocking.service

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
%attr(755,root,root) %{_sbindir}/lvmchange
%attr(755,root,root) %{_sbindir}/lvmconf
%attr(755,root,root) %{_sbindir}/lvmconfig
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
%attr(755,root,root) %{_sbindir}/vgmerge
%attr(755,root,root) %{_sbindir}/vgmknodes
%attr(755,root,root) %{_sbindir}/vgreduce
%attr(755,root,root) %{_sbindir}/vgremove
%attr(755,root,root) %{_sbindir}/vgrename
%attr(755,root,root) %{_sbindir}/vgs
%attr(755,root,root) %{_sbindir}/vgscan
%attr(755,root,root) %{_sbindir}/vgsplit
%{_mandir}/man5/lvm.conf.5*
%{_mandir}/man7/lvmcache.7*
%{_mandir}/man7/lvmsystemid.7*
%{_mandir}/man7/lvmthin.7*
%{_mandir}/man8/blkdeactivate.8*
%{_mandir}/man8/fsadm.8*
%{_mandir}/man8/lvchange.8*
%{_mandir}/man8/lvconvert.8*
%{_mandir}/man8/lvcreate.8*
%{_mandir}/man8/lvdisplay.8*
%{_mandir}/man8/lvextend.8*
%{_mandir}/man8/lvm-config.8
%{_mandir}/man8/lvm-dumpconfig.8
%{_mandir}/man8/lvm-lvpoll.8*
%{_mandir}/man8/lvm.8*
%{_mandir}/man8/lvmchange.8*
%{_mandir}/man8/lvmconf.8*
%{_mandir}/man8/lvmconfig.8*
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
%{systemdtmpfilesdir}/lvm2.conf
%{systemdunitdir}/blk-availability.service
%{systemdunitdir}/lvm2-monitor.service
%{systemdunitdir}/lvm2-pvscan@.service
%dir %{_sysconfdir}/lvm/cache
%ghost %{_sysconfdir}/lvm/cache/.cache
%attr(754,root,root) /etc/rc.d/init.d/blk-availability
%attr(754,root,root) /etc/rc.d/init.d/lvm2-monitor
%attr(700,root,root) %dir /run/lvm
%attr(700,root,root) %dir /var/lock/lvm
%if %{with lvmetad}
%attr(755,root,root) %{_sbindir}/lvmetad
/lib/udev/rules.d/69-dm-lvm-metad.rules
%attr(754,root,root) /etc/rc.d/init.d/lvm2-lvmetad
%{systemdunitdir}/lvm2-lvmetad.service
%{systemdunitdir}/lvm2-lvmetad.socket
%{_mandir}/man8/lvmetad.8*
%endif
%if %{with lvmlockd}
%attr(755,root,root) %{_sbindir}/lvmlockctl
%attr(755,root,root) %{_sbindir}/lvmlockd
%{systemdunitdir}/lvm2-lvmlockd.service
%{systemdunitdir}/lvm2-lvmlocking.service
%{_mandir}/man8/lvmlockctl.8*
%{_mandir}/man8/lvmlockd.8*
%endif
%if %{with lvmpolld}
%attr(755,root,root) %{_sbindir}/lvmpolld
%attr(754,root,root) /etc/rc.d/init.d/lvm2-lvmpolld
%{systemdunitdir}/lvm2-lvmpolld.service
%{systemdunitdir}/lvm2-lvmpolld.socket
%{_mandir}/man8/lvmpolld.8*
%endif

%if %{with cluster}
%files clvmd
%defattr(644,root,root,755)
%attr(755,root,root) %{_usrsbindir}/clvmd
%attr(754,root,root) /etc/rc.d/init.d/clvmd
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/clvmd
%attr(755,root,root) /lib/systemd/lvm2-cluster-activation
%{systemdunitdir}/clvmd.service
%{systemdunitdir}/lvm2-cluster-activation.service
%{systemdunitdir}/lvm2-clvmd.service
%{_mandir}/man8/clvmd.8*

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
%{py3_sitedir}/lvmdbusd
%config(noreplace) %verify(not md5 mtime size) /etc/dbus-1/system.d/com.redhat.lvmdbus1.conf
%{_datadir}/dbus-1/system-services/com.redhat.lvmdbus1.service
%{systemdunitdir}/lvm2-lvmdbusd.service
%{_mandir}/man8/lvmdbusd.8*
%endif

%files resource-agents
%defattr(644,root,root,755)
%dir %{_prefix}/lib/ocf/resource.d/lvm2
%attr(755,root,root) %{_prefix}/lib/ocf/resource.d/lvm2/VolumeGroup

%if %{with python2}
%files -n python-lvm
%defattr(644,root,root,755)
%attr(755,root,root) %{py_sitedir}/lvm.so
%{py_sitedir}/lvm-%{version}_*-py*.egg-info
%endif

%if %{with python3}
%files -n python3-lvm
%defattr(644,root,root,755)
%attr(755,root,root) %{py3_sitedir}/lvm.cpython-*.so
%{py3_sitedir}/lvm-%{version}_*-py*.egg-info
%endif

%files -n device-mapper
%defattr(644,root,root,755)
%doc *_DM
%{systemdunitdir}/dm-event.service
%{systemdunitdir}/dm-event.socket
/lib/udev/rules.d/10-dm.rules
/lib/udev/rules.d/11-dm-lvm.rules
/lib/udev/rules.d/13-dm-disk.rules
/lib/udev/rules.d/95-dm-notify.rules
%attr(755,root,root) %{_sbindir}/dmeventd
%attr(755,root,root) %{_sbindir}/dmsetup
%attr(755,root,root) %{_sbindir}/dmstats
%attr(755,root,root) %{_libdir}/libdevmapper-event-lvm2mirror.so
%attr(755,root,root) %{_libdir}/libdevmapper-event-lvm2raid.so
%attr(755,root,root) %{_libdir}/libdevmapper-event-lvm2snapshot.so
%attr(755,root,root) %{_libdir}/libdevmapper-event-lvm2thin.so
%dir %{_libdir}/device-mapper
%attr(755,root,root) %{_libdir}/device-mapper/libdevmapper-event-lvm2mirror.so
%attr(755,root,root) %{_libdir}/device-mapper/libdevmapper-event-lvm2raid.so
%attr(755,root,root) %{_libdir}/device-mapper/libdevmapper-event-lvm2snapshot.so
%attr(755,root,root) %{_libdir}/device-mapper/libdevmapper-event-lvm2thin.so
%{_mandir}/man8/dmsetup.8*
%{_mandir}/man8/dmstats.8*
%{_mandir}/man8/dmeventd.8*

%files -n device-mapper-libs
%defattr(644,root,root,755)
%attr(755,root,root) /%{_lib}/libdevmapper.so.*.*
%attr(755,root,root) /%{_lib}/libdevmapper-event.so.*.*
%attr(755,root,root) /%{_lib}/libdevmapper-event-lvm2.so.*.*
%attr(755,root,root) /%{_lib}/liblvm2app.so.*.*
%attr(755,root,root) /%{_lib}/liblvm2cmd.so.*.*

%files -n device-mapper-devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libdevmapper.so
%attr(755,root,root) %{_libdir}/libdevmapper-event.so
%attr(755,root,root) %{_libdir}/libdevmapper-event-lvm2.so
%attr(755,root,root) %{_libdir}/liblvm2app.so
%attr(755,root,root) %{_libdir}/liblvm2cmd.so
%{_includedir}/libdevmapper.h
%{_includedir}/libdevmapper-event.h
%{_includedir}/lvm2app.h
%{_includedir}/lvm2cmd.h
%{_pkgconfigdir}/devmapper.pc
%{_pkgconfigdir}/devmapper-event.pc
%{_pkgconfigdir}/lvm2app.pc

%files -n device-mapper-static
%defattr(644,root,root,755)
%{_libdir}/libdevmapper.a

%if %{with initrd}
%if %{with dietlibc}
%files -n device-mapper-dietlibc
%defattr(644,root,root,755)
%{dietlibdir}/libdevmapper.a
%endif

%files -n device-mapper-initrd
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/initrd/dmsetup

%files initrd
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/initrd/lvm
%endif
