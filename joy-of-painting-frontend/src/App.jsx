import { useState, useEffect } from 'react';
import { Tab } from '@headlessui/react';
import { PaintBrushIcon, TagIcon, CalendarIcon } from '@heroicons/react/24/outline';
import axios from 'axios';

function classNames(...classes) {
  return classes.filter(Boolean).join(' ')
}

export default function App() {
  const [filters, setFilters] = useState(null);
  const [episodes, setEpisodes] = useState([]);
  const [selectedColors, setSelectedColors] = useState([]);
  const [selectedSubjects, setSelectedSubjects] = useState([]);
  const [selectedMonths, setSelectedMonths] = useState([]);
  const [filterType, setFilterType] = useState('AND');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchFilters();
  }, []);

  const fetchFilters = async () => {
    try {
      const response = await axios.get('http://127.0.0.1:5000/api/filters');
      setFilters(response.data);
    } catch (error) {
      console.error('Error fetching filters:', error);
    }
  };

  const searchEpisodes = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      selectedColors.forEach(color => params.append('color', color));
      selectedSubjects.forEach(subject => params.append('subject', subject));
      selectedMonths.forEach(month => params.append('month', month));
      params.append('filter_type', filterType);

      const response = await axios.get(`http://127.0.0.1:5000/api/episodes?${params}`);
      setEpisodes(response.data.episodes);
    } catch (error) {
      console.error('Error searching episodes:', error);
    }
    setLoading(false);
  };

  const toggleFilter = (value, setSelected) => {
    setSelected(prev => 
      prev.includes(value)
        ? prev.filter(item => item !== value)
        : [...prev, value]
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="sticky top-0 bg-white shadow-md z-10">
        <div className="max-w-7xl mx-auto py-4 px-6 sm:px-8">
          <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">
            The Joy of Painting Episode Finder 🎨
          </h1>
        </div>
      </header>
  
      <main className="max-w-7xl mx-auto py-8 sm:px-6 lg:px-8">
        <div className="bg-white rounded-lg shadow-lg p-6">
          {/* Filter Dropdown */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">Filter Type</label>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            >
              <option value="AND">Match All Filters (AND)</option>
              <option value="OR">Match Any Filter (OR)</option>
            </select>
          </div>
  
          {/* Tabs */}
          <Tab.Group>
            <Tab.List className="flex p-1 space-x-2 bg-gray-100 rounded-lg">
              {['Colors', 'Subjects', 'Months'].map((tab) => (
                <Tab key={tab} className={({ selected }) =>
                  classNames(
                    'w-full py-2 px-4 text-sm font-medium text-center rounded-lg focus:outline-none transition',
                    selected ? 'bg-indigo-500 text-white shadow' : 'text-gray-700 hover:bg-indigo-100'
                  )
                }>
                  {tab}
                </Tab>
              ))}
            </Tab.List>
  
            <Tab.Panels className="mt-4">
              {/* Colors */}
              <Tab.Panel className="grid grid-cols-3 sm:grid-cols-4 lg:grid-cols-6 gap-4">
                {filters?.colors.map((color) => (
                  <button
                    key={color.name}
                    onClick={() => toggleFilter(color.name, selectedColors, setSelectedColors)}
                    className={classNames(
                      'w-full aspect-square rounded-lg transition transform hover:scale-105',
                      selectedColors.includes(color.name)
                        ? 'ring-4 ring-indigo-500'
                        : 'hover:shadow'
                    )}
                    style={{
                      backgroundColor: color.hex_code,
                      color: parseInt(color.hex_code.slice(1), 16) > 0xffffff / 2 ? '#000' : '#fff',
                    }}
                  >
                    {color.name}
                  </button>
                ))}
              </Tab.Panel>
  
              {/* Subjects */}
              <Tab.Panel className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                {filters?.subjects.map((subject) => (
                  <button
                    key={subject.name}
                    onClick={() => toggleFilter(subject.name, selectedSubjects, setSelectedSubjects)}
                    className={classNames(
                      'w-full px-4 py-2 rounded-md shadow text-sm font-medium text-center transition',
                      selectedSubjects.includes(subject.name)
                        ? 'bg-indigo-500 text-white'
                        : 'bg-gray-100 hover:bg-indigo-100'
                    )}
                  >
                    {subject.name}
                  </button>
                ))}
              </Tab.Panel>
  
              {/* Months */}
              <Tab.Panel className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                {filters?.months.map((month) => (
                  <button
                    key={month.month_num}
                    onClick={() => toggleFilter(month.month_num, selectedMonths, setSelectedMonths)}
                    className={classNames(
                      'w-full px-4 py-2 rounded-md shadow text-sm font-medium text-center transition',
                      selectedMonths.includes(month.month_num)
                        ? 'bg-indigo-500 text-white'
                        : 'bg-gray-100 hover:bg-indigo-100'
                    )}
                  >
                    {month.month_name.trim()}
                  </button>
                ))}
              </Tab.Panel>
            </Tab.Panels>
          </Tab.Group>
  
          {/* Search Button */}
          <div className="mt-8">
            <button
              onClick={searchEpisodes}
              disabled={loading}
              className={classNames(
                'w-full flex justify-center py-2 px-4 rounded-md shadow-sm text-sm font-medium transition',
                loading
                  ? 'bg-gray-400 text-gray-200 cursor-not-allowed'
                  : 'bg-indigo-500 text-white hover:bg-indigo-600'
              )}
            >
              {loading ? 'Searching...' : 'Search Episodes'}
            </button>
          </div>
        </div>
  
        {/* Episodes */}
        <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {episodes.map((episode) => (
            <div key={episode.episode_id} className="bg-white rounded-lg shadow-lg overflow-hidden">
              <div className="p-6">
                <h3 className="text-lg font-semibold text-gray-900">{episode.title}</h3>
                {episode.youtube_src && (
                  <div className="mt-4 aspect-video">
                    <iframe
                      className="w-full h-full rounded"
                      src={episode.youtube_src}
                      title={episode.title}
                      frameBorder="0"
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                      allowFullScreen
                    ></iframe>
                  </div>
                )}
                <p className="mt-2 text-sm text-gray-500">{episode.season} {episode.episode} - {episode.air_date}</p>
  
                <div className="mt-4">
                  <h4 className="text-sm font-medium text-gray-900">Colors</h4>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {episode.colors.map((color) => {
                      const colorObj = filters?.colors.find((c) => c.name === color);
                      return (
                        <span
                          key={color}
                          className="inline-block w-6 h-6 rounded-full"
                          style={{
                            backgroundColor: colorObj?.hex_code || '#gray-100',
                            border: '2px solid white',
                          }}
                        ></span>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}  