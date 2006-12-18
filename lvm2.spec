#
# Conditional build:
%bcond_without	initrd	# don't build initrd version
%bcond_without	uClibc	# link initrd version with static glibc instead of uClibc
%bcond_without	clvmd	# do not build clvmd
%bcond_without	selinux	# disable SELinux
#
%ifarch %{x8664} sparc64 sparc
%undefine	with_uClibc
%endif
Summary:	The new version of Logical Volume Manager for Linux
Summary(pl):	Nowa wersja Logical Volume Managera dla Linuksa
Name:		lvm2
Version:	2.01.15
Release:	1.1
License:	GPL
Group:		Applications/System
Source0:	ftp://sources.redhat.com/pub/lvm2/LVM2.%{version}.tgz
# Source0-md5:	c71654baff263254fb5a226624ee8ef3
%define	devmapper_ver	1.01.05
Source1:	ftp://sources.redhat.com/pub/dm/device-mapper.%{devmapper_ver}.tgz
# Source1-md5:	074cf116cc2c7194f2d100bc5f743833
URL:		http://sources.redhat.com/lvm2/
Patch0:		%{name}-sscanf.patch
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	device-mapper-devel >= %{devmapper_ver}
%{?with_selinux:BuildRequires:	libselinux-devel >= 1.10}
BuildRequires:	rpmbuild(macros) >= 1.213
%if %{with initrd}
%{!?with_uClibc:BuildRequires:	glibc-static}
%{?with_uClibc:BuildRequires:	uClibc-static >= 0.9.26}
%endif
%if %{with clvmd}
BuildRequires:	ccs-devel
BuildRequires:	dlm-devel >= 1.0-0.pre21.2
BuildRequires:	gulm-devel >= 1.0-0.pre26.2
%endif
BuildRequires:	readline-devel
Requires:	device-mapper
Requires:	dlm >= 1.0-0.pre21.2
%{?with_clvmd:Requires:	gulm >= 1.0-0.pre26.2}
%{?with_selinux:Requires:	libselinux >= 1.10}
Obsoletes:	lvm
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sbindir	/sbin
%define		_libdir		/%{_lib}

%description
This package includes a number of utilities for creating, checking,
and repairing logical volumes.

%description -l pl
Pakiet ten zawiera narzêdzia do tworzenia, sprawdzania i naprawiania
logicznych wolumenów dyskowych (LVM2).

%package initrd
Summary:	The new version of Logical Volume Manager for Linux - initrd version
Summary(pl):	Nowa wersja Logical Volume Managera dla Linuksa - wersja dla initrd
Group:		Base

%description initrd
This package includes a number of utilities for creating, checking,
and repairing logical volumes - staticaly linked for initrd.

%description initrd -l pl
Pakiet ten zawiera narzêdzia do tworzenia, sprawdzania i naprawiania
logicznych wolumenów dyskowych (LVM2) - statycznie skonsolidowane na
potrzeby initrd.

%prep
%setup -q -n LVM2.%{version} -a1
%patch0 -p1

%build
cp -f /usr/share/automake/config.sub autoconf
%{__aclocal}
%{__autoconf}

%if %{with initrd}
dm=$(ls -1d device-mapper*)
cd $dm
# no selinux for initrd
sed -i -e 's#AC_CHECK_LIB(selinux.*##g' configure.in
cp -f /usr/share/automake/config.sub autoconf
%{__aclocal}
%{__autoconf}
%configure \
        %{?with_uClibc:CC="%{_target_cpu}-uclibc-gcc"} \
	--with-optimisation="-Os" \
        --with-interface=ioctl \
	--disable-nls
unset CFLAGS || :
%{__make}
ar cru libdevmapper.a lib/ioctl/*.o lib/*.o
ranlib libdevmapper.a
cd ..
%configure \
	CFLAGS="-I$(pwd)/${dm}/include -DINITRD_WRAPPER=1" \
	%{?with_uClibc:CC="%{_target_cpu}-uclibc-gcc"} \
	ac_cv_lib_dl_dlopen=no \
	--with-optimisation="-Os" \
	--enable-static_link \
	--with-lvm1=internal \
	--disable-selinux \
	--disable-nls
%{__make} \
	LDFLAGS+="-L$(pwd)/${dm} -L$(pwd)/lib"
mv -f tools/lvm.static initrd-lvm
%{__make} clean
%endif

%configure \
	CFLAGS="%{rpmcflags}" \
	--enable-readline \
	--enable-fsadm \
	%{?with_clvmd:--with-clvmd} \
	--with-lvm1=internal \
	--with-pool=internal \
	--with-cluster=internal \
	--with-snapshots=internal \
	--with-mirrors=internal \
	%{!?with_selinux:--disable-selinux}
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_sysconfdir}/lvm

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	OWNER="" \
	GROUP=""

touch $RPM_BUILD_ROOT%{_sysconfdir}/lvm/lvm.conf

%{?with_initrd:install initrd-lvm $RPM_BUILD_ROOT%{_sbindir}/initrd-lvm}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README WHATS_NEW doc/*
%attr(755,root,root) %{_sbindir}/*
%{?with_initrd:%exclude %{_sbindir}/initrd-lvm}
%{_mandir}/man?/*
%attr(750,root,root) %dir %{_sysconfdir}/lvm
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/lvm/lvm.conf

%if %{with initrd}
%files initrd
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/initrd-lvm
%endif
