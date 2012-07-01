# TODO
# - vgscan --ignorelocking failure creates /var/lock/lvm (even if /var is not yet mounted)
# - --with-replicators (=internal/shared/none, default is none)?
# - OCF agents?
#
# Conditional build:
%bcond_without	initrd		# don't build initrd version
%bcond_without	uClibc		# link initrd version with uClibc
%bcond_with	dietlibc	# link initrd version with dietlibc
%bcond_with	glibc		# link initrd version with static GLIBC
%bcond_without  cluster		# disable all cluster support (clvmd&cmirrord)
%bcond_without  cman		# disable cman cluster support (clvmd)
%bcond_without	corosync	# disable corosync cluster support (clvmd&cmirrord)
%bcond_without	openais		# disable openais cluster support (clvmd)
%bcond_with	lvmetad		# enable lvmetad
%bcond_without	selinux		# disable SELinux

%ifarch sparc64 sparc
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

%if %{without cman} && %{without corosync} && %{without openais}
%undefine	with_cluster
%endif

Summary:	The new version of Logical Volume Manager for Linux
Summary(pl.UTF-8):	Nowa wersja Logical Volume Managera dla Linuksa
Name:		lvm2
Version:	2.02.95
Release:	10
License:	GPL v2
Group:		Applications/System
Source0:	ftp://sources.redhat.com/pub/lvm2/LVM2.%{version}.tgz
# Source0-md5:	bd470a802046c807603618a443732ea7
Source1:	%{name}-tmpfiles.conf
Patch0:		%{name}-selinux.patch
Patch1:		%{name}-diet.patch
Patch2:		device-mapper-dmsetup-export.patch
Patch3:		%{name}-clvmd_init.patch
Patch4:		dl-dlsym.patch
Patch5:		pldize_lvm2_monitor.patch
Patch6:		%{name}-wrapper.patch
Patch7:		udev-deprecated.patch
URL:		http://sources.redhat.com/lvm2/
BuildRequires:	autoconf >= 2.61
BuildRequires:	automake
%{?with_selinux:BuildRequires:	libselinux-devel >= 1.10}
%{?with_selinux:BuildRequires:	libsepol-devel}
BuildRequires:	ncurses-devel
BuildRequires:	pkgconfig
BuildRequires:	readline-devel
BuildRequires:	rpmbuild(macros) >= 1.647
BuildRequires:	udev-devel >= 143
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
%{?with_cman:BuildRequires:	cluster-cman-devel}
BuildRequires:	cluster-dlm-devel
%if %{with corosync} || %{with openais}
BuildRequires:	corosync-devel
%endif
%{?with_openais:BuildRequires:	openais-devel >= 1.0}
%endif
Requires(post,preun,postun):	systemd-units >= 38
Requires:	device-mapper >= %{version}-%{release}
%{?with_selinux:Requires:	libselinux >= 1.10}
Requires:	systemd-units >= 38
# doesn't work with 2.4 kernels
Requires:	uname(release) >= 2.6
Obsoletes:	lvm
Obsoletes:	lvm2-systemd
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sbindir	/sbin
%define		_usrsbindir	/usr/sbin

# changing CFLAGS in the middle confuses confcache
%undefine	configure_cache

# borken on AC
%define		filterout_ld	-Wl,--as-needed

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

%description clvmd
clvmd is the daemon that distributes  LVM  metadata  updates  around
a cluster.   It must be running on all nodes in the cluster and will
give an error if a node in the cluster does not have this daemon
running.

%description clvmd -l pl.UTF-8
clvmd to demon który rozprowadza zmiany meta-danych LVM po klastrze.
Mysi działać na wszystkich węzłach klastra i zgłosi błąd gdy
jakiś węzeł w klastrze nie ma tego demona uruchomionego.

%package cmirrord
Summary:	Cluster mirror log daemon
Group:		Applications/System
Requires:	cluster-cman

%description cmirrord
cmirrord is the daemon that tracks mirror log information in a cluster.
It is specific to device-mapper based mirrors (and by extension, LVM cluster
mirrors). Cluster mirrors are not possible without this daemon running.

This daemon relies on the cluster infrastructure provided by the Cluster
MANager (CMAN), which must be set up and running in order for cmirrord to
function.

%package -n device-mapper
Summary:	Userspace support for the device-mapper
Summary(pl.UTF-8):	Wsparcie dla mapowania urządzeń w przestrzeni użytkownika
Group:		Base
Requires(post,preun,postun):	systemd-units >= 38
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

%package -n device-mapper-devel
Summary:	Header files and development documentation for %{name}
Summary(pl.UTF-8):	Pliki nagłówkowe i dokumentacja do %{name}
Group:		Development/Libraries
Requires:	device-mapper = %{version}-%{release}
%if %{with selinux}
Requires:	libselinux-devel
Requires:	libsepol-devel
%endif

%description -n device-mapper-devel
Header files and development documentation for %{name}.

%description -n device-mapper-devel -l pl.UTF-8
Pliki nagłówkowe i dokumentacja do %{name}.

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
%patch5 -p1
%patch6 -p1
%patch7 -p1

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
	--with-optimisation="%{rpmcflags} -Os" \
	--enable-static_link \
	--with-lvm1=internal \
	--disable-selinux \
	--%{?with_glibc:en}%{!?with_glibc:dis}able-selinux \
	--disable-readline \
	--disable-nls
# glibc version links with normal static libdevicemapper which has selinux enabled
# and we need to keep these in sync between device-mapper and lvm2

%{__sed} -i -e 's#rpl_malloc#malloc#g' lib/misc/configure.h
%{__sed} -i -e 's#rpl_realloc#realloc#g' lib/misc/configure.h

%{__make} -j1 -C include
%{__make} -j1 -C lib LIB_SHARED= VERSIONED_SHLIB=
%{__make} -j1 -C libdm LIB_SHARED= VERSIONED_SHLIB=
%{__make} -j1 -C tools dmsetup.static lvm.static %{?with_dietlibc:DIETLIBC_LIBS="-lcompat"}
mv -f tools/lvm.static initrd-lvm
mv -f tools/dmsetup.static initrd-dmsetup

# check if tools works
for tool in initrd-lvm initrd-dmsetup; do
	LVM_SYSTEM_DIR=$(pwd) ./$tool help && rc=$? || rc=$?
	if [ $rc -gt 127 ]; then
		echo >&2 "Unexpected failure (exit status: $rc) from $tool. Does this tool work?!"
		exit 1
	fi
done


%{?with_dietlibc:mv -f libdm/ioctl/libdevmapper.a diet-libdevmapper.a}
%{__make} clean

unset CC
%endif

%configure \
	--with-usrlibdir=%{_libdir} \
	%{?debug:--enable-debug} \
	--with-optimisation="%{rpmcflags}" \
	--enable-readline \
	--enable-fsadm \
	--enable-applib \
	--enable-cmdlib \
	%{?with_lvmetad:--enable-lvmetad} \
	--enable-dmeventd \
	--with-dmeventd-path=%{_sbindir}/dmeventd \
	--enable-pkgconfig \
	--enable-udev_sync \
	--enable-udev_rules \
%if %{with cluster}
	%{?with_corosync:--enable-cmirrord} \
	--with-clvmd=%{?with_cman:cman,}%{?with_openais:openais,}%{?with_corosync:corosync} \
%endif
	--with-lvm1=internal \
	--with-pool=internal \
	--with-cluster=internal \
	--with-snapshots=internal \
	--with-mirrors=internal \
	--with-thin=internal \
	--with-interface=ioctl \
	--with-udev-prefix=/ \
	--with-systemd_dir=%{systemdunitdir} \
	%{!?with_selinux:--disable-selinux}

%{__make} -j1
%{__make} -j1 -C libdm LIB_STATIC=libdevmapper.a

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/%{_lib},%{_sysconfdir}/lvm}
%{?with_dietlibc:install -d $RPM_BUILD_ROOT%{dietlibdir}}

%{__make} install install_system_dirs install_systemd_units install_initscripts \
	DESTDIR=$RPM_BUILD_ROOT \
	OWNER="" \
	GROUP=""

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/tmpfiles.d
install -m 0644 %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/tmpfiles.d/%{name}.conf

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

%preun
%systemd_preun lvm2-monitor.service

%postun
if [ "$1" = "0" ]; then
	%service lvm2-monitor stop
	/sbin/chkconfig --del lvm2-monitor
fi
%systemd_reload

%triggerpostun -- %{name} < 2.02.94-1
%systemd_trigger lvm2-monitor.service

%post -n device-mapper
/sbin/ldconfig
%systemd_post dm-event.socket

%preun -n device-mapper
%systemd_preun dm-event.socket dm-event.service

%postun -n device-mapper
/sbin/ldconfig
%systemd_reload

%triggerpostun -n device-mapper -- device-mapper < 2.02.94-1
%systemd_trigger dm-event.socket

%files
%defattr(644,root,root,755)
%doc README WHATS_NEW doc/*
%attr(755,root,root) %{_sbindir}/fsadm
%attr(755,root,root) %{_sbindir}/lv*
%attr(755,root,root) %{_sbindir}/pv*
%attr(755,root,root) %{_sbindir}/vg*
%{_mandir}/man5/lvm.conf.5*
%{_mandir}/man8/fsadm.8*
%{_mandir}/man8/lv*.8*
%{_mandir}/man8/pv*.8*
%{_mandir}/man8/vg*.8*
%attr(750,root,root) %dir %{_sysconfdir}/lvm
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/lvm/lvm.conf
%{_sysconfdir}/tmpfiles.d/lvm2.conf
%{systemdunitdir}/lvm2-monitor.service
%dir %{_sysconfdir}/lvm/cache
%ghost %{_sysconfdir}/lvm/cache/.cache
%attr(754,root,root) /etc/rc.d/init.d/lvm2-monitor

%if %{with cluster}
%files clvmd
%defattr(644,root,root,755)
%attr(755,root,root) %{_usrsbindir}/clvmd
%attr(754,root,root) /etc/rc.d/init.d/clvmd
%{_mandir}/man8/clvmd.8*

%if %{with corosync}
%files cmirrord
%defattr(644,root,root,755)
%attr(755,root,root) %{_usrsbindir}/cmirrord
%{_mandir}/man8/cmirrord.8*
%attr(754,root,root) /etc/rc.d/init.d/cmirrord
%endif
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
%attr(755,root,root) /%{_lib}/libdevmapper*.so.*.*
%attr(755,root,root) /%{_lib}/liblvm2app.so.*.*
%attr(755,root,root) /%{_lib}/liblvm2cmd.so.*.*
%dir %{_libdir}/device-mapper
%attr(755,root,root) %{_libdir}/device-mapper/*.so
%attr(755,root,root) %{_libdir}/libdevmapper-event-*.so
%{_mandir}/man8/dmsetup.8*
%{_mandir}/man8/dmeventd.8*

%files -n device-mapper-devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libdevmapper.so
%attr(755,root,root) %{_libdir}/libdevmapper-event.so
%attr(755,root,root) %{_libdir}/liblvm2app.so
%attr(755,root,root) %{_libdir}/liblvm2cmd.so
%{_includedir}/libdevmapper*.h
%{_includedir}/lvm2app.h
%{_includedir}/lvm2cmd.h
%{_pkgconfigdir}/devmapper*.pc
%{_pkgconfigdir}/lvm2app.pc

%files -n device-mapper-static
%defattr(644,root,root,755)
%{_libdir}/libdevmapper*.a

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
