#
# Conditional build:
%bcond_without	initrd	# don't build initrd version
%bcond_without	uClibc	# link initrd version with static glibc instead of uClibc
#
%ifarch amd64
%undefine	with_uClibc
%endif
Summary:	The new version of Logical Volume Manager for Linux
Summary(pl):	Nowa wersja Logical Volume Managera dla Linuksa
Name:		lvm2
Version:	2.00.17
Release:	1
License:	GPL
Group:		Applications/System
Source0:	ftp://sources.redhat.com/pub/lvm2/LVM2.%{version}.tgz
# Source0-md5:	f1a17894ccedc9b55a1f62e6f08a4c4f
%define	devmapper_ver	1.00.18
Source1:	ftp://sources.redhat.com/pub/dm/device-mapper.%{devmapper_ver}.tgz
# Source1-md5:	ff14891c9a717731289355c334056eb4
Patch0:		%{name}-opt.patch
Patch1:		%{name}-initrd.patch
Patch2:		device-mapper-opt.patch
URL:		http://sources.redhat.com/lvm2/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	device-mapper-devel >= 1.00.07
BuildRequires:	libselinux-devel >= 1.10
%if %{with initrd}
%{!?with_uClibc:BuildRequires:	glibc-static}
%{?with_uClibc:BuildRequires:	uClibc-static >= 0.9.26}
%endif
Requires:	device-mapper
Requires:	libselinux >= 1.10
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

%if %{with initrd}
cd `ls -1d device-mapper*`
%patch2 -p1
%endif

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
        %{?with_uClibc:CC="%{_target_cpu}-uclibc-gcc -Os"} \
        --with-interface=ioctl
unset CFLAGS || :
%{__make}
ar cru libdevmapper.a lib/ioctl/*.o lib/*.o
ranlib libdevmapper.a
cd ..
cp configure.in configure.in-selinux-enabled
# no selinux for initrd
sed -i -e 's#AC_CHECK_LIB(selinux.*##g' configure.in
%{__aclocal}
%{__autoconf}
%configure \
	%{?with_uClibc:CC="%{_target_cpu}-uclibc-gcc -Os"} \
	--enable-static_link \
	--with-lvm1=internal
%{__make} \
	CFLAGS="-I$(pwd)/${dm}/include -DINITRD_WRAPPER=1 -DHAVE_GETOPTLONG=1" \
	LD_FLAGS="-L$(pwd)/${dm} -L$(pwd)/lib -static"
mv -f tools/lvm initrd-lvm
%{__make} clean
mv configure.in-selinux-enabled configure.in
rm -rf autom4te.cache config.cache
%endif

%{__aclocal}
%{__autoconf}
%configure \
	CFLAGS="%{rpmcflags} -DHAVE_GETOPTLONG=1" \
	--with-lvm1=internal
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
%attr(755,root,root) %{_sbindir}/[elpv]*
%{_mandir}/man?/*
%attr(750,root,root) %dir %{_sysconfdir}/lvm
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/lvm/lvm.conf

%if %{with initrd}
%files initrd
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/initrd-lvm
%endif
