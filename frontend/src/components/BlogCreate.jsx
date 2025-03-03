import { useState, useCallback, useEffect, useMemo } from "react";
import defaultblogpic from '../assets/Images/selectcover.png'
import JoditEditor from "jodit-react";
import Cookies from 'js-cookie';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
const BlogCreate = () => {
    const [logs, setLogs] = useState([]);
    const [coverImage, setCoverImage] = useState(null);
    const [content, setContent] = useState('')
    const [title, setTitle] = useState('');
    const [category, setCategory] = useState('');
    const clearFormFields = () => {
        setCoverImage(null);
        setContent('');
        setTitle('');
        setCategory('');
    };
    const handleFileChange = (e) => {
        const file = e.target.files[0];
        setCoverImage(file);
    };

    const appendLog = useCallback(
        (message) => {
            console.log("logs = ", logs);
            const newLogs = [...logs, message];
            setLogs(newLogs);
        },
        [logs, setLogs]
    );

    const config = useMemo(
        () => ({
            readonly: false
        }),
        []
    );

    const onChange = useCallback(
        (newContent) => {
            appendLog(`onChange triggered with ${newContent}`);
        },
        [appendLog]
    );

    useEffect(() => {
        console.log("onChange = ", onChange);
    }, [onChange]);

    const onBlur = useCallback(
        (newContent) => {
            appendLog(`onBlur triggered with ${newContent}`);
            setContent(newContent);
        },
        [appendLog, setContent]
    );

    const handleSubmit = async (e) => {
        e.preventDefault();

        const formData = new FormData();
        formData.append('title', title);
        formData.append('category', category);
        formData.append('content', content);
        formData.append('cover_image', coverImage);

        try {
            const response = await fetch('http://127.0.0.1:8000/create/', {
                method: 'POST',
                headers: {
                    Authorization: `Bearer ${Cookies.get('new_access_token')}`,
                },
                body: formData,
            });

            if (response.ok) {
                const data = await response.json();
                console.log('Blog created successfully', data);
                toast.success('Blog sent for review!', {
                    position: toast.POSITION.TOP_RIGHT,
                });
                clearFormFields();
                // navigate('/home');
            } else if (response.status === 401) {
                const new_refresh_token = Cookies.get('new_refresh_token')
                const refreshResponse = await fetch(
                    'http://127.0.0.1:8000/api/users/token/refresh/',
                    {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ refresh: new_refresh_token }),
                        credentials: 'include',
                    });

                if (refreshResponse.ok) {
                    const data = await refreshResponse.json();
                    const newAccessToken = data.access_token;
                    Cookies.set('new_access_token', newAccessToken);
                    handleSubmit(e);
                }
            } else {
                const errorData = await response.json();
                console.error('Error creating blog', errorData);
                toast.error('Error creating blog. Please try again.', {
                    position: toast.POSITION.TOP_RIGHT,
                });
            }
        } catch (error) {
            console.error('Error creating blog', error);
        }
    };


    return (
        <div>
            <ToastContainer />
            <section className="body-font relative max-w-screen-lg mx-auto">
                <div className="container px-5 py-24 mx-auto">
                    <div className="flex flex-col w-full mb-3">
                        <h1 className="xl:text-3xl sm:text-2xl text-xl font-semibold mb-4 "> <span className='text-blue'>Create</span> and <span className='text-blue'>Customise</span> your blog here!</h1>
                        <img
                            src={coverImage ? URL.createObjectURL(coverImage) : defaultblogpic}
                            alt="Cover"
                            className="md:h-84 w-full mx-auto my-2 object-contain"
                            style={{ maxHeight: '300px', maxWidth: '100%' }}
                        />
                    </div>
                    <form className="mx-auto" onSubmit={handleSubmit}>
                        <div className="flex flex-wrap -m-2">
                            <div className='p-2 w-full right-0'>
                                <h2 className='pb-5'>Select a cover image for your blog</h2>
                                <input
                                    type="file"
                                    accept="image/*"
                                    alt="img"
                                    name="cover_image"
                                    id="cover_image"
                                    onChange={handleFileChange}
                                    className="mt-1 p-2 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm"
                                />
                            </div>
                            <div className="p-2 w-full">
                                <div className="relative">
                                    <input
                                        type="text"
                                        placeholder='Title of your blog'
                                        id="title"
                                        name="title"
                                        value={title}
                                        onChange={(e) => setTitle(e.target.value)}
                                        className="w-full bg-gray-200 rounded border text-base outline-none text-gray-700 py-1 px-3 leading-8 transition-colors duration-200 ease-in-out"
                                    />
                                </div>
                            </div>
                            <div className="p-2 w-full">
                                <div className="relative">
                                    <select
                                        id="category"
                                        name="category"
                                        value={category}
                                        onChange={(e) => setCategory(Array.from(e.target.selectedOptions, option => option.value))}
                                        className="w-1/3 bg-gray-200 rounded border text-base outline-none text-gray-700 py-2 px-3 leading-8 transition-colors duration-200 ease-in-out focus:ring-2 focus:ring-blue-400"
                                    >
                                        <option value="" disabled className="text-gray-500">Select a category</option>
                                        <option value="category1" className="text-lg m-2 bg-white p-2">Category 1</option>
                                        <option value="category2" className="text-lg m-2 bg-white p-2">Category 2</option>
                                        <option value="category3" className="text-lg m-2 bg-white p-2">Category 3</option>
                                        <option value="category4" className="text-lg m-2 bg-white p-2">Category 4</option>
                                    </select>
                                </div>
                            </div>
                            <div className="p-2 w-full">
                                <div className="relative text-primary">
                                    <JoditEditor
                                        value={content}
                                        config={config}
                                        tabIndex={1}
                                        onBlur={onBlur}
                                        onChange={onChange}
                                    />
                                </div>
                            </div>
                            <div className="p-2 w-full">
                                <button type="submit" className='flex mx-auto bg-blue px-3  rounded-md py-2 text-base text-white border border-blue mt-2'>Publish Blog</button>
                            </div>
                            <div className="p-2 w-full pt-8 mt-8 border-t border-gray-200 text-center" />
                        </div>
                    </form>
                </div>
            </section>
        </div>
    )
}

export default BlogCreate
