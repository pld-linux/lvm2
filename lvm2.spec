#
# Conditional build:
%bcond_without	initrd	# don't build initrd version
Summary:	The new version of Logical Volume Manager for Linux
Summary(pl):	Nowa wersja Logical Volume Managera dla Linuksa
Name:		lvm2
Version:	2.00.09
Release:	1
License:	GPL
Group:		Applications/System
Source0:	ftp://sources.redhat.com/pub/lvm2/LVM2.%{version}.tgz
# Source0-md5:	661cf8914e2227ad615a29f3eb106a4d
%define	devmapper_ver	1.00.09
Source1:	ftp://sources.redhat.com/pub/dm//device-mapper.%{devmapper_ver}.tgz
# Source1-md5:	c08c9478d7176a4ba2de1707baa41909
Patch0:		%{name}-opt.patch
Patch1:		%{name}-initrd.patch
Patch2:		%{name}-gkh.patch
URL:		http://sources.redhat.com/lvm2/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	device-mapper-devel >= 1.00.07
%{?with_initrd:BuildRequires:	uClibc-static >= 0.9.26}
Requires:	device-mapper
Obsoletes:	lvm
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_sbindir	/sbin
%define		_libdir		/lib

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
%patch1 -p1
%patch2 -p1

%build
cp -f /usr/share/automake/config.sub autoconf
%{__aclocal}
%{__autoconf}

%if %{with initrd}
dm=$(ls -1d device-mapper*)
cd $dm
cp -f /usr/share/automake/config.sub autoconf
%{__aclocal}
%{__autoconf}
%configure \
        CC="%{_target_cpu}-uclibc-gcc -Os" \
        --with-interface=ioctl \
        --with-kernel-dir=nothing
%{__make} \
	CFLAGS="-DCONFIG_DM_IOCTL_V4=1 "
ar cru libdevmapper.a lib/ioctl/*.o lib/*.o
ranlib libdevmapper.a
cd ..
%configure \
	CC="%{_target_cpu}-uclibc-gcc -Os" \
	--enable-static_link \
	--with-lvm1=internal
%{__make} \
	CFLAGS="-I$(pwd)/${dm}/include -DINITRD_WRAPPER=1 -DCONFIG_DM_IOCTL_V4=1 -DHAVE_GETOPTLONG=1" \
	LD_FLAGS="-L$(pwd)/${dm} -L$(pwd)/lib -static"
mv -f tools/lvm initrd-lvm
%{__make} clean
rm -f config.cache
%endif

%configure \
	CFLAGS="-DCONFIG_DM_IOCTL_V4=1 -DHAVE_GETOPTLONG=1" \
	--with-lvm1=internal
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_sysconfdir}/lvm

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	OWNER=$(id -u) \
	GROUP=$(id -g)

touch $RPM_BUILD_ROOT%{_sysconfdir}/lvm/lvm.conf

%{?with_initrd:install initrd-lvm $RPM_BUILD_ROOT%{_sbindir}/initrd-lvm}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README WHATS_NEW doc/*
%attr(755,root,root) %{_sbindir}/[elpv]*
%{_mandir}/man?/*
%attr(750,root,root) %dir %{_sysconfdir}/lvm
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/lvm/lvm.conf

%if %{with initrd}
%files initrd
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/initrd-lvm
%endif
