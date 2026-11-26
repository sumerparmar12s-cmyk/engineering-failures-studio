cd /home/user/engineering-failures-studio/episodes/titan-submersible/real
B=https://archive.org/download/uscg-titan-submersible-hearings
for f in "Testimony Media/CG 001_1 TITAN_Animation 20240915_v2.2.mp4" "Testimony Media/04_ROV Titan Submersible Tail Cone.mp4" "Testimony Media/07_ROV Titan Submersible Aft Dome Aft Ring Hull Remnants.mp4" "Testimony Media/DOD_110564587.mp4" "Testimony Media/DOD_110579329.mp4" "Testimony Media/DOD_110579650.mp4" "May 2025 Update/Testimony Media/DOD_111016570.mp4" "May 2025 Update/Testimony Media/DOD_110804017.mp4" "NTSB Titan Docket - DCA23FM036/attachment1_SFCchartanimation-Rel.mp4" "Testimony Media/DOD_109728593.mp4"; do
  o=$(basename "$f" | tr ' ' '_'); u="$B/$(python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$f")"
  curl -sL --retry 3 -o "$o" "$u" && echo "OK $o $(du -m "$o"|cut -f1)MB"
done
curl -sL -o titanic_1912_footage.mp4 "https://archive.org/download/titanic-disaster-genuine-footage-1911-1912/Titanic_Disaster_-_Genuine_Footage_(1911-1912).mp4" && echo OK titanic
echo IA DONE
