# TODO
# - vgscan --ignorelocking failure creates /var/lock/lvm (even if /var is not yet mounted)
#
# Conditional build:
%bcond_without	initrd		# don't build initrd version
%bcond_with	uClibc			# link initrd version with uClibc
%bcond_without	dietlibc	# link initrd version with dietlibc
%bcond_with	glibc			# link initrd version with static GLIBC
%bcond_without	clvmd		# don't build clvmd
%bcond_with	clvmd3			# build clvmd for 3rd generation of cluster
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

%if %{with clvmd3}
%undefine	with_clvmd
%endif

Summary:	The new version of Logical Volume Manager for Linux
Summary(pl.UTF-8):	Nowa wersja Logical Volume Managera dla Linuksa
Name:		lvm2
Version:	2.02.84
Release:	1
License:	GPL v2
Group:		Applications/System
Source0:	ftp://sources.redhat.com/pub/lvm2/LVM2.%{version}.tgz
# Source0-md5:	8b4e0897ee48f02c0dff11940e44e23b
Source1:	%{name}-initramfs-hook
Source2:	%{name}-initramfs-local-top
Patch0:		%{name}-selinux.patch
Patch1:		%{name}-diet.patch
Patch2:		device-mapper-dmsetup-export.patch
Patch3:		%{name}-clvmd_init.patch
Patch4:		dl-dlsym.patch
URL:		http://sources.redhat.com/lvm2/
BuildRequires:	autoconf
BuildRequires:	automake
%{?with_selinux:BuildRequires:	libselinux-devel >= 1.10}
%{?with_selinux:BuildRequires:	libsepol-devel}
BuildRequires:	pkgconfig
BuildRequires:	rpmbuild(macros) >= 1.213
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
%if %{with clvmd}
BuildRequires:	cman-devel >= 1.0
BuildRequires:	dlm-devel >= 1.0-0.pre21.2
%endif
%if %{with clvmd3}
BuildRequires:	cluster-cman-devel
BuildRequires:	cluster-dlm-devel
%endif
BuildRequires:	ncurses-devel
BuildRequires:	readline-devel
Requires:	device-mapper >= %{version}-%{release}
%if %{with clvmd}
Requires:	cman-libs >= 1.0
Requires:	dlm >= 1.0-0.pre21.2
%endif
%if %{with clvmd3}
Requires:	cluster-cman-libs
Requires:	cluster-dlm
%endif
%{?with_selinux:Requires:	libselinux >= 1.10}
# doesn't work with 2.4 kernels
Requires:	uname(release) >= 2.6
Obsoletes:	lvm
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

%package -n device-mapper
Summary:	Userspace support for the device-mapper
Summary(pl.UTF-8):	Wsparcie dla mapowania urządzeń w przestrzeni użytkownika
Group:		Base

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

%package initramfs
Summary:	The new version of Logical Volume Manager for Linux - support scripts for initramfs-tools
Summary(pl.UTF-8):	Nowa wersja Logical Volume Managera dla Linuksa - skrypty dla initramfs-tools
Group:		Base
Requires:	%{name} = %{version}-%{release}
Requires:	initramfs-tools

%description initramfs
The new version of Logical Volume Manager for Linux - support scripts
for initramfs-tools.

%description initramfs -l pl.UTF-8
Nowa wersja Logical Volume Managera dla Linuksa - skrypty dla
initramfs-tools.

%prep
%setup -q -n LVM2.%{version}
%{?with_selinux:%patch0 -p1}
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1

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
%{?with_dietlibc:export CC="diet %{__cc}"}

%configure \
	ac_cv_lib_dl_dlopen=no \
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
	--enable-cmdlib \
	--enable-dmeventd \
	--enable-pkgconfig \
	%{?with_clvmd:--with-clvmd=cman} \
	--with-lvm1=internal \
	--with-pool=internal \
	--with-cluster=internal \
	--with-snapshots=internal \
	--with-mirrors=internal \
	--with-interface=ioctl \
	%{!?with_selinux:--disable-selinux}
%{__make} -j1
%{__make} -j1 -C libdm LIB_STATIC=libdevmapper.a

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/%{_lib},%{_sysconfdir}/lvm} \
	$RPM_BUILD_ROOT%{_datadir}/initramfs-tools/{hooks,scripts/local-top}
%{?with_dietlibc:install -d $RPM_BUILD_ROOT%{dietlibdir}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	OWNER="" \
	GROUP=""

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

install -p %{SOURCE1} $RPM_BUILD_ROOT%{_datadir}/initramfs-tools/hooks/lvm2
install -p %{SOURCE2} $RPM_BUILD_ROOT%{_datadir}/initramfs-tools/scripts/local-top/lvm2

cp -a libdm/libdevmapper.a $RPM_BUILD_ROOT%{_libdir}

%clean
rm -rf $RPM_BUILD_ROOT

%post   -n device-mapper -p /sbin/ldconfig
%postun -n device-mapper -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc README WHATS_NEW doc/*
%attr(755,root,root) %{_sbindir}/fsadm
%attr(755,root,root) %{_sbindir}/lv*
%attr(755,root,root) %{_sbindir}/pv*
%attr(755,root,root) %{_sbindir}/vg*
%{?with_clvmd:%attr(755,root,root) %{_usrsbindir}/clvmd}
%{_mandir}/man5/lvm.conf.5*
%{?with_clvmd:%{_mandir}/man8/clvmd.8*}
%{_mandir}/man8/fsadm.8*
%{_mandir}/man8/lv*.8*
%{_mandir}/man8/pv*.8*
%{_mandir}/man8/vg*.8*
%attr(750,root,root) %dir %{_sysconfdir}/lvm
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/lvm/lvm.conf

%files -n device-mapper
%defattr(644,root,root,755)
%doc *_DM
%attr(755,root,root) %{_sbindir}/dmeventd
%attr(755,root,root) %{_sbindir}/dmsetup
%attr(755,root,root) /%{_lib}/libdevmapper*.so.*.*
%attr(755,root,root) /%{_lib}/liblvm2cmd.so.*.*
%dir %{_libdir}/device-mapper
%attr(755,root,root) %{_libdir}/device-mapper/*.so
%{_mandir}/man8/dmsetup.8*
%{_mandir}/man8/dmeventd.8*

%files -n device-mapper-devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libdevmapper*.so
%attr(755,root,root) %{_libdir}/liblvm2cmd.so
%{_includedir}/libdevmapper*.h
%{_includedir}/lvm2cmd.h
%{_pkgconfigdir}/devmapper*.pc

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

%files initramfs
%defattr(644,root,root,755)
%attr(755,root,root) %{_datadir}/initramfs-tools/hooks/lvm2
%attr(755,root,root) %{_datadir}/initramfs-tools/scripts/local-top/lvm2
